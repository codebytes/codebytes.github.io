---
title: "Stop Losing the Bug When You Restart Aspire"
date: "2026-10-09T09:00:00-04:00"
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

[Aspire Field Notes](/series/aspire-field-notes/) starts with that problem: keeping a failure around long enough to investigate it after the app has moved on.

## Healthy resources, failed request

A failed business request doesn't have to show up in `/health`. When a downstream dependency rejects a call, the request fails while the service keeps running and its health endpoint stays green.

{{< field-notes-request-path >}}

Green indicators tell you the processes are running and passing their health checks. To diagnose the failed request, you need its downstream calls, durations, and errors.

So before changing code, make sure the application emits that telemetry. The dashboard can receive OpenTelemetry, but it can't invent spans the app never produced. For .NET, Service Defaults is a good start. Node, Java, Python, and Rust services need their own instrumentation.

## Choose the right kind of persistence

Aspire 13.6 uses SQLite for dashboard storage. Its three modes have different purposes:[^persistence]

| Mode     | Storage behavior                                                  | When I would use it                          |
| -------- | ----------------------------------------------------------------- | -------------------------------------------- |
| `None`   | A temporary database for one dashboard process                    | A disposable standalone diagnostic session   |
| `Run`    | A separate database for each dashboard run, with a run selector   | Comparing a failing run with a later attempt |
| `Resume` | One database reused across restarts, without separate run history | Continuing a standalone dashboard session    |

When the AppHost launches the dashboard, it uses `Run` by default. You don't need to add a database resource to get this behavior.

A standalone dashboard still defaults to `None`. To pick up where it left off after a restart, start it with `aspire dashboard run --persistence Resume` and a stable `--application-name`. Keep the name, data directory, and mode the same each time. `Resume` keeps adding to one database, so it won't give you separate runs to compare. Only one dashboard process can write to it at a time.

## Capture a baseline, a failure, and a recovery

The [companion catalog app](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes) is small. A Vite frontend named `web` calls a catalog API named `api`. The API reads PostgreSQL's `catalogdb`, then makes one instrumented HTTP call to a separate `inventory` service, with no retry to hide a failure.

A development-only switch, `Inventory__FaultEnabled`, makes inventory return a 503 while its health endpoint stays green. Flipping it gives you a failure and a recovery to compare without breaking anything shared. Here you already know the cause. With a real bug, the trace has to support whatever fix you propose.

If you're following along, [walkthrough 01](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/01-keep-the-failing-run) has the commands and links to the one-time setup, including the database secret. The sample targets Aspire 13.6.1 and requires Aspire CLI 13.6 or later.

### A request you can repeat

Use the same request for each run. The companion's AppHost adds a **Load catalog** command to `web` that sends one `GET /api/catalog` through the frontend, the same path the browser takes. It reports the HTTP status, trace ID, and response. You can use the highlighted button in the dashboard or run `aspire resource web load-catalog` from a terminal. Here's the abridged registration:

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

With the fault off, **Load catalog** returns a 200 and three products. That's your baseline.

### Reproduce the failure

Restart the same app with the fault on and run **Load catalog** again. The frontend, API, inventory service, and database remain healthy, but the command fails with `HTTP 503: Inventory unavailable` and a trace ID:

{{< figure src="load-catalog-503.png" alt="Aspire dashboard Resources page with the Load catalog action highlighted on the web resource and a failure notification reading HTTP 503: Inventory unavailable, with the request's trace ID" caption="The resources are healthy, but Load catalog returns HTTP 503." figureClass="full-width" >}}

Open that trace. It has four spans: the API's request, its PostgreSQL query, one HTTP call to inventory, and inventory's own span. All three HTTP spans show 503, and there's only one client span, so nothing retried the call:

{{< figure src="failed-trace.png" alt="Trace detail for GET /api/catalog showing the API request, its PostgreSQL query to catalogdb, one HTTP GET call that returned 503, and the inventory service's GET /inventory span" caption="The database query completes. The inventory call returns 503, and the API passes that failure back." figureClass="full-width" >}}

Before stopping the failing run, open the dashboard's **Console logs** page for both `api` and `inventory`. **The dashboard stores a console stream in a run's history only after you view or export it there.** Reading the same output in a terminal with `aspire logs` doesn't count. Structured logs sent through OpenTelemetry are stored either way.[^persistence]

That's easy to miss when a startup message is the clue you need.

CLI queries such as `aspire otel traces --has-error` read the live run. Picking a historical run in the browser doesn't change what the CLI sees, so do the comparison below in the dashboard.

### Keep the failure and compare recovery

Open the run selector in the dashboard header. Hover or focus the **Live run** row to reveal **Pin run**, then pin the failing run. Stop the app, turn the fault off, start it again, and run **Load catalog**. The request returns a 200 and three products through the same call path.

{{< field-notes-run-history >}}

In the new dashboard, the run selector lists the pinned failing run beside the live one:

{{< figure src="pinned-run-selector.png" alt="Run selector open in the recovered dashboard, listing the live run and the pinned 10:08:18 PM failing run" caption="The pinned failure is still available beside the new live run." figureClass="full-width" >}}

Select the pinned run. Its failed trace and the `api` and `inventory` **Console logs** you viewed earlier are still there:

{{< figure src="pinned-run-console.png" alt="Console logs for api in the pinned 10:08:18 PM run, filtered to 503, ending with the warning that inventory returned HTTP 503 with no retry, followed by the same trace ID" caption="The historical API console contains the original 503 and its trace ID." figureClass="full-width" >}}

History is on by default. Pinning only protects a run from being pruned.

Change one thing between runs. If you update packages, request data, storage, and the fault setting at once, you won't know which change mattered.

Go into the comparison with a question:

| Question                        | What to compare                                                           |
| ------------------------------- | ------------------------------------------------------------------------- |
| Did the request succeed?        | The application's result, not just resource health                        |
| Did the failure move elsewhere? | Errors and span relationships across the request                          |
| Did a retry hide the problem?   | Downstream attempts and elapsed time, where instrumented                  |
| Did the environment change?     | Resource properties, endpoints, and configuration relevant to the failure |

Be careful with duration alone. A faster second request might reflect warmed caches or connection pools rather than the fix.

## How much history the dashboard keeps

By default, the dashboard keeps up to 10 unpinned runs per application and prunes the oldest when a new run starts. Pinned runs don't count toward that limit.[^persistence]

History is tracked by the dashboard's application name, not the checkout path. Two clones of the same AppHost share one history and the same 10-run limit. A burst of runs in one checkout can prune an unpinned reproduction from the other.

Each run's database also caps console logs, structured logs, and traces at 100,000 each by default, shared across resources. Metric points have their own limit. If a run exceeds those caps, its oldest data is gone, pinned or not.

Those caps count records, not bytes. Large attributes and high-cardinality metrics still use disk space, and deleted rows free space inside the database file without shrinking it.

Unpin runs when you've finished investigating. If you need longer retention, use a telemetry backend with a retention policy and backups.

## What a historical run can tell you

Historical runs are read-only. You can't restart resources from last Tuesday's run, change an old parameter, or replay a request from its trace.

The dashboard starts watching the AppHost's resources only when a page first needs them. A run that nobody opens in a browser can keep traces and structured logs but no resource snapshot.[^client] When there is a snapshot, it shows the resources' latest state, not every change during the run.

Upgrades can strand old runs. The dashboard doesn't migrate its schema. A `Run` database from an incompatible version stays in the selector but won't open, and an incompatible `Resume` database is replaced. Before upgrading Aspire, save anything you still need from an old run.[^persistence]

If you need to inspect or copy a database, include SQLite's write-ahead log files, and don't edit it with outside tools.

## Under the hood: SQLite and Native AOT

James Newton-King's persistence deep dive explains the design. SQLite runs inside the dashboard process, with no database server to manage. Dapper queries filter, count, sort, and page telemetry in the database, so the dashboard doesn't hold a run's whole history as live .NET objects.[^persistence-design]

In his large-telemetry test, private memory dropped from about 1,007 MB in Aspire 13.5 to 241 MB in 13.6. He measured each version once, after a forced garbage collection. Expect different numbers from this sample and from your own apps.

The 13.6 dashboard also ships as a Native AOT executable. His AOT write-up covers the work across Blazor, Fluent UI, serialization, and Dapper. For this workflow, the payoff is less startup and JIT work each time you stop and start the dashboard.[^aot] Dapper.AOT ties the two changes together by generating query and mapping code at build time.[^persistence-design]

Two caveats if you're tempted to try Native AOT in your own app:

- The native dashboard doesn't need a separately installed .NET runtime, but the Aspire CLI still makes sure one is available for the rest of Aspire.
- The dashboard's experimental Blazor AOT work doesn't make Native AOT a supported publishing option for Blazor Web Apps in general.

## Protect what you keep

Resource snapshots and telemetry can contain credentials, user data, and internal addresses. A value the dashboard masks on screen is still stored unredacted in the database.

The dashboard doesn't add database authentication, encryption at rest, replication, or backups, so protect the data directory and any copies. Redact anything you share with a colleague, attach to an issue, or hand to an external tool.

For production retention and access control, use Application Insights or another telemetry backend built for that job.

## Try this before the next refactor

A normal stop leaves dashboard history in place, so the pinned run is still there when you come back.

Next time you chase a bug, capture the failing request and pin its run before you change any code. After the fix, repeat the same request and compare the two traces. You'll have something better to show in the review than "it worked after I restarted."

{{% if-published "/posts/aspire-field-notes-model-the-whole-app" %}}
[Next: model the whole application](/posts/aspire-field-notes-model-the-whole-app/) so configuration, readiness, and telemetry describe the same system.
{{% /if-published %}}

[^release]: Maddy Montaquila, [Aspire 13.6: Your dashboard gets memory](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/), September 29, 2026.

[^persistence]: [Dashboard persistence modes, captured data, retention, compatibility, and security](https://aspire.dev/dashboard/data-persistence/).

[^persistence-design]: James Newton-King, [Adding persistence to the Aspire dashboard](https://devblogs.microsoft.com/aspire/aspire-dashboard-persistence/), October 8, 2026.

[^client]: The 13.6.1 dashboard's [`DashboardClient`](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Dashboard/ServiceClient/DashboardClient.cs) connects to the AppHost's resource service on first use, then watches resources for the dashboard's lifetime.

[^aot]: James Newton-King, [Bringing Native AOT to the Aspire dashboard](https://devblogs.microsoft.com/aspire/aspire-dashboard-native-aot/), October 6, 2026.
