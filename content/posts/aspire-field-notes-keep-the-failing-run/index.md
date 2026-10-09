---
title: "Stop Losing the Bug When You Restart Aspire"
date: "2026-10-07T09:00:00-04:00"
lastmod: "2026-10-08T23:04:45-04:00"
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
description: "Keep a failing Aspire run, restart the app, and compare the traces. A catalog example shows what the 13.6 dashboard saves and what you need to capture yourself."
---

You reproduce an intermittent failure, change one line, and restart the application. This time the request works. Now you need the old trace to work out why.

If it disappeared with the restart, you're left comparing the new run with whatever you remember. Aspire 13.6's dashboard keeps completed runs, so you can go back to the failed request instead.[^release]

<!--more-->

This is where [Aspire Field Notes](/series/aspire-field-notes/) starts: keeping enough of a failure to investigate it after the app has moved on.

## A green dashboard is not the result

A failure in a business request does not have to show up in `/health`. When a downstream dependency rejects a call, the request fails while the service keeps running and its health endpoint stays healthy.

A resource graph full of green indicators tells us about process and health state. To diagnose the failed request, we need its downstream calls, durations, and errors.

Before changing code, make sure the application emits that evidence. The dashboard can receive OpenTelemetry, but it cannot reconstruct spans that the application never produced. For .NET, Service Defaults is a useful starting point. Node, Java, Python, and Rust still need the appropriate instrumentation.

## Choose the right kind of persistence

Aspire 13.6 uses SQLite for dashboard storage. Its three modes have different purposes:[^persistence]

| Mode     | Storage behavior                                                  | When I would use it                          |
| -------- | ----------------------------------------------------------------- | -------------------------------------------- |
| `None`   | A temporary database for one dashboard process                    | A disposable standalone diagnostic session   |
| `Run`    | A separate database for each dashboard run, with a run selector   | Comparing a failing run with a later attempt |
| `Resume` | One database reused across restarts, without separate run history | Continuing a standalone dashboard session    |

An **AppHost-launched dashboard uses `Run` by default**. You do not need to add a database resource to your application to get this behavior.

A **standalone dashboard still defaults to `None`**. To continue from the same database across restarts, start it with `aspire dashboard run --persistence Resume` and a stable `--application-name`. Keep the application name, data directory, and mode consistent. `Resume` is not the setting for before-and-after run comparison; it continues one database. Only one process can write that resumed database at a time.

## Capture a baseline, a failure, and recovery

The [companion catalog app](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes) gives us a repeatable request: a Vite frontend named `web` calls a catalog API named `api`, which reads PostgreSQL's `catalogdb` and calls a separate `inventory` service. There is one instrumented HTTP call to inventory, with no retry to hide a failure.

A development-only switch, `Inventory__FaultEnabled`, makes inventory return a 503 while its health endpoint stays green. Turning it off lets us compare failure and recovery without breaking a shared dependency. We know the cause in this example; with an actual bug, the trace would need to support the proposed fix.

If you're following along, [walkthrough 01](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/01-keep-the-failing-run) has the setup and one-time database secret. The sample targets Aspire 13.6.1 and requires Aspire CLI 13.6 or later.

### A request you can repeat

Use the same request for each run. The companion's AppHost adds a **Load catalog** command to `web` that sends one `GET /api/catalog` through the frontend, following the browser's path. It reports the HTTP status, trace ID, and response. You can use the highlighted button in the dashboard or run `aspire resource web load-catalog` from a terminal. Here's the abridged registration:

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

The [full registration](https://github.com/codebytes/blog-samples/blob/main/aspire-field-notes/catalog/Catalog.AppHost/AppHost.cs) also reports a non-success status as a failed command, so a broken request never looks like a passing one.

With the fault off, **Load catalog** returns a 200 and three products. That is the baseline.

### Reproduce the failure

Restart the same app with the fault on and run **Load catalog** again. The frontend, API, inventory service, and database remain healthy, but the command fails with `HTTP 503: Inventory unavailable` and a trace ID. That's the expected result with the fault enabled:

{{< figure src="load-catalog-503.png" alt="Aspire dashboard Resources page with the Load catalog action highlighted on the web resource and a failure notification reading HTTP 503: Inventory unavailable, with the request's trace ID" caption="The resources are healthy, but Load catalog returns HTTP 503." figureClass="full-width" >}}

Open that trace. You should see the API's request, its PostgreSQL query, exactly one HTTP call to inventory, and inventory's own span, with 503 on the three HTTP spans. The single inventory client span confirms that this request wasn't retried:

{{< figure src="failed-trace.png" alt="Trace detail for GET /api/catalog showing the API request, its PostgreSQL query to catalogdb, one HTTP GET call that returned 503, and the inventory service's GET /inventory span" caption="The database query completes; the inventory call returns 503 and the API passes that failure back." figureClass="full-width" >}}

Before stopping the failing run, open the dashboard's **Console logs** page for both `api` and `inventory`. **A console stream is stored in history only after you view or export it in the dashboard.** Reading it with `aspire logs` doesn't capture it there. Structured logs sent through OpenTelemetry are stored separately.[^persistence]

This is easy to miss when a startup message is the clue you need. Open the relevant console pages while the run is live, even if you've already read the output in your terminal.

AppHost-scoped CLI queries, such as `aspire otel traces --has-error`, read the live run. Selecting a historical run in the browser does not change what a separate CLI command sees, so use the dashboard's run selector for the comparison below.

### Keep the failure and compare recovery

Open the run selector in the dashboard header. Hover or focus the **Live run** row to reveal **Pin run**, then pin the failing run. Stop the app, turn the fault off, start it again, and run **Load catalog**. The request returns a 200 and three products through the same call path.

In the new dashboard, the run selector lists the pinned failing run beside the live one:

{{< figure src="pinned-run-selector.png" alt="Run selector open in the recovered dashboard, listing the live run and the pinned 10:08:18 PM failing run" caption="The pinned failure is still available beside the new live run." figureClass="full-width" >}}

Select the pinned run. Its failed trace and the `api` and `inventory` **Console logs** you viewed earlier are still there:

{{< figure src="pinned-run-console.png" alt="Console logs for api in the pinned 10:08:18 PM run, filtered to 503, ending with Inventory returned HTTP 503; no retry and the same trace ID" caption="The historical API console contains the original 503 and its trace ID." figureClass="full-width" >}}

Pinning retains a useful run; it is not the switch that enables history.

Keep the checkout and AppHost the same between runs. Changing packages, request data, storage, and the fault setting together would make the comparison harder to interpret.

The comparison should answer a specific question:

| Question                        | Evidence to compare                                                       |
| ------------------------------- | ------------------------------------------------------------------------- |
| Did the request succeed?        | The application's result, not just resource health                        |
| Did the failure move elsewhere? | Errors and span relationships across the request                          |
| Did a retry hide the problem?   | Downstream attempts and elapsed time, where instrumented                  |
| Did the environment change?     | Resource properties, endpoints, and configuration relevant to the failure |

Be careful with duration alone. A faster second request might reflect warmed caches or connection pools rather than the fix.

## Retained does not mean unlimited

By default, the dashboard retains up to **ten unpinned runs per application**. Pinned runs do not count toward that limit.

Run history is keyed by the dashboard's application name, not by checkout path. Two clones of the same AppHost share one history and one ten-run limit, so a burst of runs in another checkout can evict an unpinned reproduction from this one.

Within a database, console logs, structured logs, and traces each have a default limit of 100,000 entries or traces, shared across resources. Metric points have their own limits. Old data can be evicted even when you keep the run.

Those limits are not disk quotas. Large attributes and high-cardinality metrics consume space. Removing rows lets SQLite reuse pages; it does not necessarily shrink the database file.

Unpin runs when you're finished with the investigation. For longer-term retention, use a telemetry backend with a retention policy and backups.

## What a historical run can tell you

Historical views are read-only. You cannot restart last Tuesday's database, change an old parameter, or replay a request by selecting its trace.

The dashboard starts watching the AppHost's resources only when a page first needs them. A run that nobody opens in a browser can therefore keep traces and structured logs without a resource snapshot.[^client] Even when captured, that snapshot won't tell you about every configuration change during the run.

Schema compatibility matters across dashboard upgrades. Incompatible historical `Run` databases can remain visible but unavailable to open. `Resume` can replace an incompatible database after reading its schema version successfully. Preserve important evidence deliberately before upgrading; do not assume persistence promises indefinite forward compatibility.[^persistence]

If you must inspect or copy a database, follow the storage guidance, including SQLite's write-ahead log files. Do not edit dashboard databases with external tools.

## Under the hood: SQLite and Native AOT

James Newton-King's persistence deep dive explains the design behind this workflow. SQLite runs inside the dashboard, without another database server to manage. Dapper queries filter, count, sort, and page the stored telemetry before materializing the requested results. Keeping a run does not require keeping its entire history as live .NET objects.[^persistence-design]

The article's large-telemetry comparison measured private memory at roughly 1,007 MB for Aspire 13.5 and 241 MB for 13.6. Its chart reports one run per version, after forced garbage collection. Those are the author's measurements for that workload, not results from this catalog sample or a promised reduction on your laptop.

The dashboard also ships as a Native AOT executable in 13.6.

James Newton-King's engineering write-up explains the work across Blazor, Fluent UI, serialization, and Dapper. The practical benefit for this workflow is less startup and first-use JIT work when you repeatedly stop and start the dashboard.[^aot]

Dapper.AOT connects the two changes by generating query and mapping code at build time for the native dashboard.[^persistence-design]

Two qualifications matter if you're considering AOT for your own app:

- The dashboard's native executable does not require a separately installed .NET runtime, but the Aspire CLI still ensures a runtime is available for other parts of Aspire.
- The dashboard's experimental Blazor AOT work does not make Native AOT a generally supported publishing option for arbitrary Blazor Web Apps.

## Protect what you keep

Resource snapshots and telemetry can contain credentials, user data, and internal addresses. A sensitive value masked in the dashboard UI can still be present in the underlying database without redaction.

The dashboard does not add database-level authentication, encryption at rest, replication, or backups. Protect the data directory and any copies. Review and redact evidence before sharing it with a colleague, attaching it to an issue, or giving an external tool access.

For production retention and access controls, use Application Insights or another appropriate telemetry backend. Local run history solves a different problem.

## Try this before the next refactor

Before changing code for the next bug, capture the request that fails and pin its run. After the change, repeat that request and compare the two traces. You'll have something more useful in the review than "it worked after I restarted."

A normal stop keeps the dashboard history, application data, and database volume, so you can come back to the pinned run later.

[Next: model the whole application](/posts/aspire-field-notes-model-the-whole-app/) so configuration, readiness, and telemetry describe the same system.

[^release]: Maddy Montaquila, [Aspire 13.6: Your dashboard gets memory](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/), September 29, 2026.

[^persistence]: [Dashboard persistence modes, captured data, retention, compatibility, and security](https://aspire.dev/dashboard/data-persistence/).

[^persistence-design]: James Newton-King, [Adding persistence to the Aspire dashboard](https://devblogs.microsoft.com/aspire/aspire-dashboard-persistence/), October 8, 2026.

[^client]: The 13.6.1 dashboard's [`DashboardClient`](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Dashboard/ServiceClient/DashboardClient.cs) connects to the AppHost's resource service on first use, then watches resources for the dashboard's lifetime.

[^aot]: James Newton-King, [Bringing Native AOT to the Aspire dashboard](https://devblogs.microsoft.com/aspire/aspire-dashboard-native-aot/), October 6, 2026.
