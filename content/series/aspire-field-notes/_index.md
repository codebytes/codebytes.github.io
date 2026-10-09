---
title: "Aspire Field Notes: A Better Developer Loop"
description: "Six Aspire 13.6 posts built around one catalog app: keep a failed trace, inspect its dependencies, guide an agent, retain data, and review a deployment."
---

An application can start cleanly and still fail its first useful request. This series follows a catalog lookup through that gap: reproducing a 503, keeping the trace, investigating the dependency, and checking the same path after a change.

**Aspire Field Notes** uses Aspire 13.6 and one small catalog app throughout. The posts explain what to look for; the companion walkthroughs provide setup and commands.

## The reading path

| Part | Post                                                                                                         | What you will do                                                                                                   |
| ---- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| 1    | [Stop Losing the Bug When You Restart Aspire](/posts/aspire-field-notes-keep-the-failing-run/)               | Preserve a failure, compare diagnostic runs, and understand what the dashboard actually retains                    |
| 2    | [A Polyglot App Is More Than a Process List](/posts/aspire-field-notes-model-the-whole-app/)                 | Connect configuration, readiness, and telemetry across languages, including the new Java and Rust hosting previews |
| 3    | [Put the Debugging Tools Next to the App](/posts/aspire-field-notes-terminals-and-repls/)                    | Inspect a database through the terminal dock and build a bounded, repeatable terminal check                        |
| 4    | [Give Your Coding Agent a Developer Loop, Not a Guess](/posts/aspire-field-notes-agents-with-evidence/)      | Scope an agent to the right AppHost and report a diagnosis grounded in runtime evidence                            |
| 5    | [One Configuration Contract, From Laptop to Container](/posts/aspire-field-notes-portable-state-and-config/) | Keep application settings stable while paths, connection names, credentials, and storage change                    |
| 6    | [Same AppHost, Different Deployment Promises](/posts/aspire-field-notes-choose-your-deployment/)             | Choose a deployment target from workload constraints rather than assume every publisher behaves alike              |

Read them in order for the full story, or start with the problem you have today. The terminal experiment in part three can be run independently.

## The application behind the examples

The code lives in the [`aspire-field-notes` collection in blog-samples](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes). The catalog has a Vite frontend named `web`, a catalog API named `api`, PostgreSQL's `catalogdb`, and a separate `inventory` service.

A development-only inventory fault makes `/api/catalog` return a 503 while resource health remains green. The `/api/state` endpoints let us save a note through `DATA_PATH` and read it after a restart. Both are local teaching examples.

Part three also has an independent Node terminal AppHost. Part six publishes Docker Compose files for review without building images or deploying. Express, Sandboxes, and the other cloud targets are comparisons with their documentation.

## Companion walkthroughs

| Part | Walkthrough                                                                                                                                                                  |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | [Baseline, failure, retained run, and recovery](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/01-keep-the-failing-run)                 |
| 2    | [Configuration, readiness, and telemetry across the catalog app](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/02-model-the-whole-app) |
| 3    | [PostgreSQL REPL and an independent terminal experiment](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/03-terminals-and-repls)         |
| 4    | [A scoped, evidence-driven agent investigation](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/04-agents-with-evidence)                 |
| 5    | [Portable configuration and retained application state](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/05-portable-state-and-config)    |
| 6    | [Compose publishing and artifact review](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/06-choose-your-deployment)                      |

Start with the [collection README](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes) for prerequisites, the clone command, and the one-time database secret. The walkthroughs require [Aspire CLI](https://aspire.dev/get-started/install-cli/) 13.6 or later; this series targets 13.6.1.

Use **Load catalog** on `web` in the dashboard, or `aspire resource web load-catalog`, to make the request and get its status and trace ID. The other helpers check state after a restart, fresh terminal output, and generated Compose routing and storage. None requires installing agent guidance.

The [official Node.js weather-map sample](https://aspire.dev/reference/samples/aspire-with-node/) is an additional example of a frontend, instrumented API, and external dependency under a TypeScript AppHost. The Java and Rust sections explain optional preview integrations; those languages are not required to run the catalog companion.

**Aspire 13.6.1** is the [first 13.6 patch](https://github.com/microsoft/aspire/releases/tag/v13.6.1), released October 7, 2026, with fixes for 13.6.0 regressions. The posts identify preview packages and experimental APIs as they come up. The companion keeps stable `AddProject` resources; there's no Project V2 migration or Azure deployment to perform.

## What this builds on

My earlier [CLI introduction](/posts/aspire-cli-getting-started/) and [deployment article](/posts/aspire-cli-part-2/) cover the original command-oriented journey. The [MCP article](/posts/aspire-cli-part-3-mcp/) and [skills, plugins, and marketplace guide](/posts/agent-skills-plugins-marketplace/) explain the agent-tooling background.

Those articles reflect their publication versions. This series uses the 13.6 documentation for current commands and behavior, particularly the move to skills-first agent setup with optional MCP.

## Sources worth exploring

- [Maddy Montaquila's 13.6 announcement](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/) and the [complete release documentation](https://aspire.dev/whats-new/aspire-13-6/) establish what shipped.
- [David Fowler's developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) explains how an application model can replace setup knowledge passed between teammates.
- [David Pine's weather-map post](https://bsky.app/profile/davidpine.dev/post/3mwmut6556k2a) points to the Node.js and React sample discussed in part two.
- [Mitch Denny's terminal deep dive](https://devblogs.microsoft.com/aspire/aspire-terminal-support/) and [James Newton-King's Native AOT dashboard article](https://devblogs.microsoft.com/aspire/aspire-dashboard-native-aot/) explain the engineering behind the new experiences.
- [James Newton-King's persistence deep dive](https://devblogs.microsoft.com/aspire/aspire-dashboard-persistence/), published October 8, explains the SQLite and Dapper design behind part one's retained runs and lower-memory telemetry queries.
