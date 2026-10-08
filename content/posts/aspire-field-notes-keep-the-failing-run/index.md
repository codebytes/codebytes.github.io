---
title: "Stop Losing the Bug When You Restart Aspire"
date: "2026-10-06"
draft: false
build:
  list: never
  render: always
sitemap:
  disable: true
robots: "noindex, nofollow"
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

## Run the companion

The [first companion walkthrough](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/walkthroughs/01-keep-the-failing-run) uses the [shared catalog application](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/catalog) in `blog-samples`.

Follow the [collection's prerequisites and review checkout instructions](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes) first. The commands in this article run from the sample checkout's `aspire-field-notes/` directory and call the `aspire` CLI directly. You need [Aspire CLI](https://aspire.dev/get-started/install-cli/) 13.6 or later; the steps assume the latest release.

Initialize the sample's PostgreSQL secret once before the first run:

```bash
node scripts/init-secret.mjs
```

The script preserves an existing value. Do not regenerate the database password between the failure and recovery runs. Aspire 13.6's isolated mode copies the original user secrets into the isolated context.

The application has a Vite frontend named `web`, a catalog API named `api`, PostgreSQL's `catalogdb`, and a separate `inventory` service. A request to `/api/catalog` reads the catalog and makes one instrumented HTTP call to inventory. There is no retry hiding the deliberate failure.

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

A **standalone dashboard still defaults to `None`**. If you want it to continue from the same database:

```bash
aspire dashboard run \
  --application-name catalog-notes --persistence Resume
```

Keep the application name, data directory, and mode consistent. `Resume` is not the setting for before-and-after run comparison; it continues one database. Only one process can write that resumed database at a time.

## Capture a baseline, a failure, and recovery

The sample uses `Inventory__FaultEnabled` to select a controlled, development-only 503. Do not create failures in a shared production dependency to try this.

A controlled fault makes the reproduction repeatable. Turning that fault off demonstrates recovery; it does not prove that you diagnosed an unknown bug. In a real investigation, the proposed fix still needs to address the observed cause.

### Establish the healthy baseline

```bash
Inventory__FaultEnabled=false aspire start \
  --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj \
  --isolated --non-interactive &&
aspire wait api --status healthy --timeout 120 \
  --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj --non-interactive &&
node scripts/smoke.mjs healthy
```

The smoke check discovers the current `web` endpoint, waits for the relevant health checks, and makes one same-origin `/api/catalog` request. It expects a successful response with three products, a PostgreSQL span, and one correlated API-to-inventory HTTP call.

For the interactive version, open `web` from the dashboard and select **Load catalog**. The page shows the result and its trace ID. Use the assigned endpoint, not a port copied from another run.

### Reproduce the failure

Stop this AppHost without deleting its volumes, then start the same application with the fault enabled:

```bash
aspire stop --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj \
  --non-interactive &&
Inventory__FaultEnabled=true aspire start \
  --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj \
  --isolated --non-interactive &&
aspire wait api --status healthy --timeout 120 \
  --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj --non-interactive &&
node scripts/smoke.mjs fault
```

The expected result is a **503**, even though resource readiness passed. In `fault` mode, a passing smoke check means that it observed the intended failure, not a 200 response.

The check asserts the parent-child chain from the API server span to its HTTP client span and then inventory's server span, with 503 on all three. It captures console logs, structured logs, spans, and the request result under `artifacts/fault-<trace-id>/`. That folder is the script's own evidence copy; it does not add console logs to the dashboard's run history. Its telemetry-export wait does not retry the business request.

While the failing run is still live, open the dashboard's **Console logs** page for `api` and for `inventory`. The dashboard keeps a console stream in a run's history only after you have viewed or exported it there, and opening the dashboard is also what starts recording the run's resources. You can also select **Load catalog** in the frontend; the failed response clears any previous successful rows rather than presenting stale data as a result.

The CLI can narrow the evidence for the running AppHost too:

```bash
aspire otel traces api --has-error --limit 5 \
  --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj --non-interactive
```

That is a query against the currently running app, so run it before recovery. Selecting a historical run in the browser does not change the target of a separate CLI command. Use the dashboard's run selector for the historical comparison described below.

### Keep the failure and compare recovery

Open the run selector in the dashboard header, which shows **Live run**, and select **Pin run** on the failing run before stopping the AppHost. Then recover explicitly:

```bash
aspire stop --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj \
  --non-interactive &&
Inventory__FaultEnabled=false aspire start \
  --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj \
  --isolated --non-interactive &&
node scripts/smoke.mjs recovery
```

Open the new dashboard URL and compare its live run with the pinned failure. The request now returns 200 and three products through the same call path. In the pinned run, the failed trace and the `api` and `inventory` **Console logs** you viewed earlier should remain inspectable. Pinning retains a useful run; it is not the switch that enables history.

Keep the checkout and AppHost path the same across this walkthrough. Changing packages, request data, storage, and the fault setting together would make the comparison harder to interpret.

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

**Console logs are stored only after their stream has been viewed or exported in the dashboard.** Reading them with `aspire logs`, or copying them into an artifact folder as the companion's smoke check does, does not add them to the run's history. If nobody opened that stream, a historical run can lack the console output you expected. Structured logs sent through OpenTelemetry follow the telemetry-storage path instead.[^persistence]

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

Start with the [companion's repeatable failure](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/walkthroughs/01-keep-the-failing-run). Capture it, pin it, change one thing, and repeat the same request. Then apply that discipline to an actual bug. The useful outcome is being able to explain the difference between runs with evidence.

When you finish, stop the catalog AppHost with the collection's scoped cleanup command. A normal stop keeps the dashboard history, application data, and database volume.

[Next: model the whole application](/posts/aspire-field-notes-model-the-whole-app/) so configuration, readiness, and telemetry describe the same system.

[^release]: Maddy Montaquila, [Aspire 13.6: Your dashboard gets memory](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/), September 29, 2026.

[^persistence]: [Dashboard persistence modes, captured data, retention, compatibility, and security](https://aspire.dev/dashboard/data-persistence/).

[^client]: The 13.6.1 dashboard's [`DashboardClient`](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Dashboard/ServiceClient/DashboardClient.cs) connects to the AppHost's resource service on first use, then watches resources for the dashboard's lifetime.

[^aot]: James Newton-King, [Bringing Native AOT to the Aspire dashboard](https://devblogs.microsoft.com/aspire/aspire-dashboard-native-aot/), October 6, 2026.
