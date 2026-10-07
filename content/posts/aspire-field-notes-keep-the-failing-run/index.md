---
title: "Stop Losing the Bug When You Restart Aspire"
date: "2026-10-06"
draft: true
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
header:
  teaser: ""
  og_image: ""
excerpt_separator: "<!--more-->"
description: "Use Aspire 13.6 run history to keep a reproduction, compare a fix, and avoid confusing retained telemetry with a replayable or production-grade system."
---

Imagine reproducing an intermittent failure, changing one line, and restarting the application. The new run works. Great. But what actually changed?

If the old trace and resource state disappeared with the restart, the answer is often a screenshot, a memory, or a guess. Aspire 13.6's most useful new feature addresses that gap: the dashboard keeps completed runs so you can return to the evidence.[^release]

<!--more-->

This is part one of [Aspire Field Notes](/series/aspire-field-notes/). We are starting with a debugging problem, not with installing another tool.

## A green dashboard is not the result

Our example is a catalog application. A browser calls an API, which queries a database or another service. One request fails, but all the processes remain running.

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
aspire dashboard run --application-name catalog-notes --persistence Resume
```

Keep the application name, data directory, and mode consistent. `Resume` is not the setting for before-and-after run comparison; it continues one database. Only one process can write that resumed database at a time.

## A better failure-to-fix workflow

Use a development-only failure you control, such as a stub that returns a 503 for one catalog lookup. Do not create failures in a shared production dependency to try this.

1. **Establish the baseline.** Run the same request successfully and verify that the expected services appear in its trace.
2. **Reproduce the failure.** Keep the request inputs and record the failing trace ID, error, and relevant resource configuration.
3. **Capture the console evidence.** Open the relevant console log stream before ending the run if those logs matter to the investigation.
4. **Pin the run.** Use the dashboard's run selector to retain the reproduction before restarting.
5. **Change one thing.** Fix the suspected cause without simultaneously changing packages, retry counts, and test data.
6. **Repeat the operation.** Open the earlier run and compare it with the new one.

The comparison should answer a specific question:

| Question                        | Evidence to compare                                                       |
| ------------------------------- | ------------------------------------------------------------------------- |
| Did the request succeed?        | The application's result, not just resource health                        |
| Did the failure move elsewhere? | Errors and span relationships across the request                          |
| Did a retry hide the problem?   | Downstream attempts and elapsed time, where instrumented                  |
| Did the environment change?     | Resource properties, endpoints, and configuration relevant to the failure |

These are measurements to collect, not benchmark results from this article. A faster second request might reflect warmed caches or connection pools rather than the fix.

For a running AppHost, the CLI is another way to narrow the evidence. With an AppHost at `./AppHost/AppHost.csproj` and a resource named `api`:

```bash
aspire otel traces api --has-error true --limit 5 \
  --apphost ./AppHost/AppHost.csproj --non-interactive
```

That is a query against the selected running app. Do not assume changing the historical run in a browser silently changes the target of a separate CLI command. Use the dashboard's run selector for the historical comparison described here.

## The console-log detail that is easy to miss

Persisted history does not mean every byte written to stdout is automatically archived.

**Console logs are stored after their stream has been viewed or exported.** If nobody captured that stream, a historical run can lack the console output you expected. Structured logs sent through OpenTelemetry follow the telemetry-storage path instead.[^persistence]

This is why opening the relevant console view is part of the reproduction procedure. If an investigation depends on a startup message, capture it before stopping the app. For longer-term evidence requirements, use a logging backend designed for them.

## Retained does not mean unlimited

By default, the dashboard retains up to **ten unpinned runs per application**. Pinned runs do not count toward that limit.

Within a database, console logs, structured logs, and traces each have a default limit of 100,000 entries or traces, shared across resources. Metric points have their own limits. Old data can be evicted even when you keep the run.

Those limits are not disk quotas. Large attributes and high-cardinality metrics consume space. Removing rows lets SQLite reuse pages; it does not necessarily shrink the database file.

Treat pinning as part of an investigation's lifecycle: keep the useful reproduction, then retire it when it no longer serves a purpose. A directory full of pinned runs is not a backup strategy.

## A historical run is evidence, not a time machine

Historical views are read-only. You cannot restart last Tuesday's database, change an old parameter, or replay a request by selecting its trace.

The stored resource snapshot also is not a full application event log. It is useful context for what the dashboard retained, not proof of every configuration transition during the run.

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

Pick one local failure. Capture it, pin it, change one thing, and repeat the same request. The useful outcome is being able to explain the difference between the two runs with evidence.

[Next: model the whole application](/posts/aspire-field-notes-model-the-whole-app/) so configuration, readiness, and telemetry describe the same system.

[^release]: Maddy Montaquila, [Aspire 13.6: Your dashboard gets memory](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/), September 29, 2026.

[^persistence]: [Dashboard persistence modes, captured data, retention, compatibility, and security](https://aspire.dev/dashboard/data-persistence/).

[^aot]: James Newton-King, [Bringing Native AOT to the Aspire dashboard](https://devblogs.microsoft.com/aspire/aspire-dashboard-native-aot/), October 6, 2026.
