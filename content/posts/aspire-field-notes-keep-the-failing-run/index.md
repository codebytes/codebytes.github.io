---
title: "Stop Losing the Bug When You Restart Aspire"
date: "2026-10-06"
categories:
  - "Development"
tags:
  - "Aspire"
  - "Debugging"
  - "OpenTelemetry"
  - "Observability"
series:
  - "Aspire Field Notes"
series_order: 1
permalink: "/posts/aspire-field-notes-keep-the-failing-run/"
slug: "aspire-field-notes-keep-the-failing-run"
image: "featured.png"
featureImage: "featured.png"
header:
  teaser: "featured.png"
  og_image: "featured.png"
excerpt_separator: "<!--more-->"
description: "Use Aspire 13.6 run history to keep a reproduction, compare a fix, and avoid confusing retained telemetry with a replayable or production-grade system."
---

Imagine reproducing an intermittent failure, changing one line, and restarting the application. The new run works. Great. But what actually changed?

If the old trace and resource state disappeared with the restart, the answer is often a screenshot, a memory, or a guess. Aspire 13.6's most useful new feature addresses that gap: the dashboard keeps completed runs so you can return to the evidence.[^release]

<!--more-->

This is part one of [Aspire Field Notes](/series/aspire-field-notes/). We are starting with a debugging problem, not with installing another tool.

## The companion app

The examples use a small catalog app from the [companion samples](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes): a Vite frontend named `web`, a catalog API named `api`, a PostgreSQL database named `catalogdb`, and a separate `inventory` service. Loading the catalog reads the database and makes one instrumented HTTP call to inventory, with no retry to hide a failure.

A development-only switch, `Inventory__FaultEnabled`, makes inventory return a 503. That gives us a failure we can reproduce on demand without breaking anything shared. [Walkthrough 01](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/walkthroughs/01-keep-the-failing-run) has the setup, including the one-time database secret, and every command used here. You need [Aspire CLI](https://aspire.dev/get-started/install-cli/) 13.6 or later.

## A green dashboard is not the result

The sample's inventory fault affects a business request, not `/health`. With the fault enabled, the catalog request fails while the service remains running and its health endpoint stays healthy.

A resource graph full of green indicators tells us something about process and health state. It does not prove that the catalog request worked. We need evidence from the operation itself: the request, the downstream call, its duration, and the error.

Before changing code, make sure the application emits that evidence. The dashboard can receive OpenTelemetry, but it cannot reconstruct spans that the application never produced. For .NET, Service Defaults is a useful starting point. Node, Java, Python, and Rust still need the appropriate instrumentation.

That distinction makes retained runs valuable. We are keeping observations, not collecting reassuring colors.

## Choose the right kind of persistence

Aspire 13.6 uses SQLite for dashboard storage. Its three modes have different purposes:[^persistence]

| Mode     | What survives                                                     | When I would use it                          |
| -------- | ----------------------------------------------------------------- | -------------------------------------------- |
| `None`   | A temporary database for one dashboard process                    | A disposable standalone diagnostic session   |
| `Run`    | A separate database for each dashboard run, with a run selector   | Comparing a failing run with a later attempt |
| `Resume` | One database reused across restarts, without separate run history | Continuing a standalone dashboard session    |

An **AppHost-launched dashboard uses `Run` by default**. You do not need to add a database resource to your application to get this behavior.

A **standalone dashboard still defaults to `None`**. To continue from the same database across restarts, start it with `aspire dashboard run --persistence Resume` and a stable `--application-name`. Keep the application name, data directory, and mode consistent. `Resume` is not the setting for before-and-after run comparison; it continues one database. Only one process can write that resumed database at a time.

## Capture a baseline, a failure, and recovery

A controlled fault makes the reproduction repeatable. Turning that fault off demonstrates recovery; it does not prove that you diagnosed an unknown bug. In a real investigation, the proposed fix still needs to address the observed cause. Do not create failures in a shared production dependency to try this.

### A request you can repeat

Comparing runs only works if you make the same request each time. The companion's AppHost adds a **Load catalog** command to the `web` resource. It sends one `GET /api/catalog` request through the frontend, the same path the browser uses, and reports the HTTP status, the trace ID, and the response. It appears as a highlighted button on `web` in the dashboard, and `aspire resource web load-catalog` runs it from a terminal. An abridged version of the registration:

```csharp
web.WithHttpCommand(
    path: "/api/catalog",
    displayName: "Load catalog",
    endpointName: "http",
    commandName: "load-catalog",
    commandOptions: new HttpCommandOptions
    {
        Method = HttpMethod.Get,
        IsHighlighted = true,
        // PrepareRequest sets a ten-second timeout.
        // GetCommandResult returns the status, trace ID, and response as JSON.
    });
```

The [full registration](https://github.com/codebytes/blog-samples/blob/codebytes-aspire-companion-samples/aspire-field-notes/catalog/Catalog.AppHost/AppHost.cs) also reports a non-success status as a failed command, so a broken request never looks like a passing one.

With the fault off, **Load catalog** returns a 200 and three products. That is the baseline.

### Reproduce the failure

Restart the same app with the fault on and run **Load catalog** again. Every resource still reports **Running**, but the command fails with `HTTP 503: Inventory unavailable` and the trace ID of the request that failed. That failure is the observation you want, not a broken step:

{{< figure src="load-catalog-503.png" alt="Aspire dashboard Resources page with the Load catalog action highlighted on the web resource and a failure notification reading HTTP 503: Inventory unavailable, with the request's trace ID" figureClass="full-width" >}}

Open that trace. You should see the API's request, its PostgreSQL query, exactly one HTTP call to inventory, and inventory's own span, with 503 on the three HTTP spans. A single client span means no retry is hiding the failure. The command makes the request; reading that chain is your job:

{{< figure src="failed-trace.png" alt="Trace detail for GET /api/catalog showing the API request, its PostgreSQL query to catalogdb, one HTTP GET call that returned 503, and the inventory service's GET /inventory span" figureClass="full-width" >}}

While the failing run is still live, open the dashboard's **Console logs** page for `api` and for `inventory`. The dashboard keeps a console stream in a run's history only after you have viewed or exported it there, and opening the dashboard is also what starts recording the run's resources.

The CLI can query the same evidence, for example with `aspire otel traces --has-error`, but it always targets the running app. Selecting a historical run in the browser does not change what a separate CLI command sees, so use the dashboard's run selector for the comparison below.

### Keep the failure and compare recovery

Open the run selector in the dashboard header, which shows **Live run**, and select **Pin run** on the failing run. Then stop the app, turn the fault off, start it again, and run **Load catalog**. The request returns a 200 and three products through the same call path.

In the new dashboard, the run selector lists the pinned failing run beside the live one:

{{< figure src="pinned-run-selector.png" alt="Run selector open in the recovered dashboard, listing the live run and the pinned 10:08:18 PM failing run" figureClass="full-width" >}}

Select the pinned run. Its failed trace and the `api` and `inventory` **Console logs** you viewed earlier are still there:

{{< figure src="pinned-run-console.png" alt="Console logs for api in the pinned 10:08:18 PM run, filtered to 503, ending with Inventory returned HTTP 503; no retry and the same trace ID" figureClass="full-width" >}}

Pinning retains a useful run; it is not the switch that enables history.

Keep the checkout and AppHost the same between runs. Changing packages, request data, storage, and the fault setting together would make the comparison harder to interpret.

The comparison should answer a specific question:

| Question                        | Evidence to compare                                                       |
| ------------------------------- | ------------------------------------------------------------------------- |
| Did the request succeed?        | The application's result, not just resource health                        |
| Did the failure move elsewhere? | Errors and span relationships across the request                          |
| Did a retry hide the problem?   | Downstream attempts and elapsed time, where instrumented                  |
| Did the environment change?     | Resource properties, endpoints, and configuration relevant to the failure |

These are measurements to collect, not benchmark results from this article. A faster second request might reflect warmed caches or connection pools rather than the fix.

## The console-log detail that is easy to miss

Persisted history does not mean every byte written to stdout is automatically archived.

**Console logs are stored only after their stream has been viewed or exported in the dashboard.** Reading them with `aspire logs` does not add them to the run's history. If nobody opened that stream, a historical run can lack the console output you expected. Structured logs sent through OpenTelemetry follow the telemetry-storage path instead.[^persistence]

This is why opening the relevant **Console logs** pages is part of the reproduction procedure. If an investigation depends on a startup message, view it in the dashboard before stopping the app. For longer-term evidence requirements, use a logging backend designed for them.

## Retained does not mean unlimited

By default, the dashboard retains up to **ten unpinned runs per application**. Pinned runs do not count toward that limit.

Run history is keyed by the dashboard's application name, not by checkout path. Two clones of the same AppHost share one history and one ten-run limit, so a burst of runs in another checkout can evict an unpinned reproduction from this one.

Within a database, console logs, structured logs, and traces each have a default limit of 100,000 entries or traces, shared across resources. Metric points have their own limits. Old data can be evicted even when you keep the run.

Those limits are not disk quotas. Large attributes and high-cardinality metrics consume space. Removing rows lets SQLite reuse pages; it does not necessarily shrink the database file.

Treat pinning as part of an investigation's lifecycle: keep the useful reproduction, then retire it when it no longer serves a purpose. A directory full of pinned runs is not a backup strategy.

## A historical run is evidence, not a time machine

Historical views are read-only. You cannot restart last Tuesday's database, change an old parameter, or replay a request by selecting its trace.

The stored resource snapshot also is not a full application event log. The dashboard starts watching the AppHost's resources only when a page first needs them, so a run that nobody opens in a browser can keep traces and structured logs without any resource snapshot.[^client] When a snapshot exists, it is useful context for what the dashboard retained, not proof of every configuration transition during the run.

Schema compatibility matters across dashboard upgrades. Incompatible historical `Run` databases can remain visible but unavailable to open. `Resume` can replace an incompatible database after reading its schema version successfully. Preserve important evidence deliberately before upgrading; do not assume persistence promises indefinite forward compatibility.[^persistence]

If you must inspect or copy a database, follow the storage guidance, including SQLite's write-ahead log files. Do not edit dashboard databases with external tools.

## Why Native AOT belongs in this story

The other dashboard improvement in 13.6 is less visible: it ships as a Native AOT executable.

James Newton-King's engineering write-up explains the work across Blazor, Fluent UI, serialization, and Dapper. The practical benefit for this workflow is less startup and first-use JIT work when you repeatedly stop and start the dashboard.[^aot]

There are two boundaries worth keeping:

- The dashboard's native executable does not require a separately installed .NET runtime, but the Aspire CLI still ensures a runtime is available for other parts of Aspire.
- The dashboard's experimental Blazor AOT work does not make Native AOT a generally supported publishing option for arbitrary Blazor Web Apps.

This is not a reason to retarget the catalog API or promise a particular speedup on your laptop. It is an improvement to the tool we use to observe the application.

## Protect what you keep

Resource snapshots and telemetry can contain credentials, user data, and internal addresses. A sensitive value masked in the dashboard UI can still be present in the underlying database without redaction.

The dashboard does not add database-level authentication, encryption at rest, replication, or backups. Protect the data directory and any copies. Review and redact evidence before sharing it with a colleague, attaching it to an issue, or giving an external tool access.

For production retention and access controls, use Application Insights or another appropriate telemetry backend. Local run history solves a different problem.

## Try this before the next refactor

Start with [walkthrough 01](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/walkthroughs/01-keep-the-failing-run) and its repeatable failure. Capture it, pin it, change one thing, and repeat the same request. Then apply that discipline to an actual bug. The useful outcome is being able to explain the difference between runs with evidence.

A normal stop keeps the dashboard history, application data, and database volume, so you can come back to the pinned run later.

[Next: model the whole application](/posts/aspire-field-notes-model-the-whole-app/) so configuration, readiness, and telemetry describe the same system.

[^release]: Maddy Montaquila, [Aspire 13.6: Your dashboard gets memory](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/), September 29, 2026.

[^persistence]: [Dashboard persistence modes, captured data, retention, compatibility, and security](https://aspire.dev/dashboard/data-persistence/).

[^client]: The 13.6.1 dashboard's [`DashboardClient`](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Dashboard/ServiceClient/DashboardClient.cs) connects to the AppHost's resource service on first use, then watches resources for the dashboard's lifetime.

[^aot]: James Newton-King, [Bringing Native AOT to the Aspire dashboard](https://devblogs.microsoft.com/aspire/aspire-dashboard-native-aot/), October 6, 2026.
