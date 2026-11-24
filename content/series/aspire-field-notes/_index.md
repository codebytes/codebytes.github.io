---
title: "Aspire Field Notes: A Better Developer Loop"
description: "Follow one catalog app from Aspire 13.6 to 17: keep a failed trace, inspect its dependencies, guide an agent, retain data, and review a deployment."
---

An application can start cleanly and still fail its first useful request. This series follows a catalog lookup through that gap: reproducing a 503, keeping the trace, investigating the dependency, and checking the same path after a change.

Parts 1 through 4 use Aspire 13.6. Part 5 upgrades the same catalog app to Aspire 17 and follows a saved note across an API restart. The companion walkthroughs provide setup and commands for each version.

## The reading path

| Part | Post                                                                                                         | What you will do                                                               |
| ---- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| 1    | [Stop Losing the Bug When You Restart Aspire](/posts/aspire-field-notes-keep-the-failing-run/)               | Pin a failed run and compare its trace with the recovery.                      |
| 2    | [A Polyglot App Is More Than a Process List](/posts/aspire-field-notes-model-the-whole-app/)                 | Follow a request through Vite, .NET, and PostgreSQL.                           |
| 3    | [Put the Debugging Tools Next to the App](/posts/aspire-field-notes-terminals-and-repls/)                    | Inspect the stored rows with `psql` and repeat the check with a terminal tape. |
| 4    | [Give Your Coding Agent a Developer Loop, Not a Guess](/posts/aspire-field-notes-agents-with-evidence/)      | Have an agent explain a 503 using evidence from one request.                   |
| 5    | [One Configuration Contract, From Laptop to Container](/posts/aspire-field-notes-portable-state-and-config/) | Prove a note survives a restart and check where Compose mounts its storage.    |

The final part will cover deployment targets.

## The application behind the examples

The [Aspire 17 catalog sample](https://github.com/codebytes/blog-samples/tree/4250daac0150d3422fe33ccd1ccd4d90e570d11c/aspire-field-notes) has a Vite frontend named `web`, a catalog API named `api`, PostgreSQL's `catalogdb`, and a separate `inventory` service.

A development-only inventory fault makes `/api/catalog` return a 503 while resource health remains green. The `/api/state` endpoints let us save a note through `DATA_PATH` and read it after a restart. Both are local teaching examples.

## Companion walkthroughs

| Part | Walkthrough                                                          |
| ---- | -------------------------------------------------------------------- |
| 1    | [Baseline, failure, retained run, and recovery][walk-1]              |
| 2    | [Configuration, readiness, and telemetry across the catalog][walk-2] |
| 3    | [PostgreSQL REPL and repeatable terminal checks][walk-3]             |
| 4    | [An agent investigation scoped to one failed request][walk-4]        |
| 5    | [Portable configuration and retained application state][walk-5]      |

For Parts 1 through 4, [download the 13.6.4 sample revision][catalog-13] so the code matches the article you're reading. For Part 5, use the Aspire 17 walkthrough above. Each walkthrough links to the prerequisites and PostgreSQL secret setup for its version.

Use **Load catalog** on `web` in the dashboard, or `aspire resource web load-catalog`, to make the request and get its status and trace ID. The other helpers check state after a restart, fresh terminal output, and generated Compose routing and storage. None requires installing agent guidance.

The [official Node.js weather-map sample](https://aspire.dev/reference/samples/aspire-with-node/) is an additional example of a frontend, instrumented API, and external dependency under a TypeScript AppHost. The Java and Rust sections explain optional preview integrations; those languages are not required to run the catalog companion.

## What this builds on

My earlier [CLI introduction](/posts/aspire-cli-getting-started/) and [deployment article](/posts/aspire-cli-part-2/) cover the original command-oriented journey. The [MCP article](/posts/aspire-cli-part-3-mcp/) and [skills, plugins, and marketplace guide](/posts/agent-skills-plugins-marketplace/) explain the agent-tooling background.

Those articles reflect their publication versions. The [Aspire 17 release notes](https://aspire.dev/whats-new/aspire-17/) explain what changed in the CLI and .NET project model used in Part 5.

## Sources worth exploring

- [Maddy Montaquila's 13.6 announcement](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/) and the [complete release documentation](https://aspire.dev/whats-new/aspire-13-6/) establish what shipped.
- [David Fowler's developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) explains how an application model can replace setup knowledge passed between teammates.
- [David Pine's weather-map post](https://bsky.app/profile/davidpine.dev/post/3mwmut6556k2a) points to the Node.js and React sample discussed in part two.
- [Mitch Denny's terminal deep dive](https://devblogs.microsoft.com/aspire/aspire-terminal-support/) and [James Newton-King's Native AOT dashboard article](https://devblogs.microsoft.com/aspire/aspire-dashboard-native-aot/) explain the engineering behind the new experiences.
- [James Newton-King's persistence deep dive](https://devblogs.microsoft.com/aspire/aspire-dashboard-persistence/), published October 8, explains the SQLite and Dapper design behind part one's retained runs and lower-memory telemetry queries.

[catalog-13]: https://github.com/codebytes/blog-samples/archive/9cfa104b225e00b0ba72165b920dce7f4ce35912.zip
[walk-1]: https://github.com/codebytes/blog-samples/tree/9cfa104b225e00b0ba72165b920dce7f4ce35912/aspire-field-notes/walkthroughs/01-keep-the-failing-run
[walk-2]: https://github.com/codebytes/blog-samples/tree/9cfa104b225e00b0ba72165b920dce7f4ce35912/aspire-field-notes/walkthroughs/02-model-the-whole-app
[walk-3]: https://github.com/codebytes/blog-samples/tree/9cfa104b225e00b0ba72165b920dce7f4ce35912/aspire-field-notes/walkthroughs/03-terminals-and-repls
[walk-4]: https://github.com/codebytes/blog-samples/tree/9cfa104b225e00b0ba72165b920dce7f4ce35912/aspire-field-notes/walkthroughs/04-agents-with-evidence
[walk-5]: https://github.com/codebytes/blog-samples/tree/4250daac0150d3422fe33ccd1ccd4d90e570d11c/aspire-field-notes/walkthroughs/05-portable-state-and-config
