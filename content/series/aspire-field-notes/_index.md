---
title: "Aspire Field Notes: A Better Developer Loop"
description: "Six practical workflows for Aspire 13.6: preserve evidence, model the application, inspect dependencies, guide agents, move configuration, and choose a deployment."
---

A working demo answers one question: can the application start? A useful developer loop answers the next ones. What failed? Can someone else reproduce it? Does the fix change the right thing? What happens when this leaves my laptop?

**Aspire Field Notes** follows those questions through Aspire 13.6. This is not another installation guide or an inventory of every release-note bullet. Each post starts with a development problem, uses a specific capability to address it, and finishes with an observable result.

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

The companions live in the [`aspire-field-notes` collection in blog-samples](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes). One shared catalog application underpins all six parts: a Vite frontend named `web`, a catalog API named `api`, PostgreSQL's `catalogdb`, and a separate `inventory` service.

A deliberate inventory failure makes `/api/catalog` return a 503 while resource health remains green. A separate `/api/state` endpoint demonstrates data retained through `DATA_PATH`. These are controlled teaching scenarios, not claims of production readiness.

Part three has a small independent terminal AppHost as well as the catalog's opt-in database REPL. Part six publishes Docker Compose artifacts for review. It does not deploy cloud resources; Express, Sandboxes, and other cloud targets remain documented comparisons rather than silently provisioned dependencies.

## Companion walkthroughs

| Part | Walkthrough                                                                                                                                                                  |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | [Baseline, failure, retained run, and recovery](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/01-keep-the-failing-run)                 |
| 2    | [Configuration, readiness, and telemetry across the catalog app](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/02-model-the-whole-app) |
| 3    | [PostgreSQL REPL and an independent terminal experiment](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/03-terminals-and-repls)         |
| 4    | [A scoped, evidence-driven agent investigation](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/04-agents-with-evidence)                 |
| 5    | [Portable configuration and retained application state](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/05-portable-state-and-config)    |
| 6    | [Compose publishing and artifact review](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/06-choose-your-deployment)                      |

Each walkthrough has the setup and exact commands for its post. Start with the [collection README](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes) for prerequisites, the clone command, and the one-time database secret. You need [Aspire CLI](https://aspire.dev/get-started/install-cli/) 13.6 or later; the steps assume the latest release.

The walkthroughs check their own results. The catalog AppHost adds a **Load catalog** command to `web`, available in the dashboard and as `aspire resource web load-catalog`; it makes one request and returns the status and trace ID for you to inspect. `state-smoke.mjs` requires a new process with retained data; the terminal helper uses fresh computed markers; and the Compose reviewer checks generated routing and storage without deploying it. Optional agent-guidance setup is not required to run any of these checks.

The [official Node.js weather-map sample](https://aspire.dev/reference/samples/aspire-with-node/) is an additional example of a frontend, instrumented API, and external dependency under a TypeScript AppHost. The Java and Rust sections explain optional preview integrations; those languages are not required to run the catalog companion.

The series targets **Aspire 13.6.1**, the [first 13.6 patch](https://github.com/microsoft/aspire/releases/tag/v13.6.1), released October 7, 2026, with fixes for 13.6.0 regressions. Preview packages and experimental APIs are identified where they appear. Examples do not require migrating stable `AddProject` resources to the prerelease .NET project model, deploying Azure resources, or giving an agent access to credentials.

## What this builds on

My earlier [CLI introduction](/posts/aspire-cli-getting-started/) and [deployment article](/posts/aspire-cli-part-2/) cover the original command-oriented journey. The [MCP article](/posts/aspire-cli-part-3-mcp/) and [skills, plugins, and marketplace guide](/posts/agent-skills-plugins-marketplace/) explain the agent-tooling background.

Those articles reflect their publication versions. This series uses the 13.6 documentation for current commands and behavior, particularly the move to skills-first agent setup with optional MCP.

Detailed retry-policy design and AI-provider selection deserve their own space. Here, resilience is something to investigate with evidence, and AI is a participant in the developer loop rather than an excuse to repeat a provider comparison.

## Sources worth exploring

- [Maddy Montaquila's 13.6 announcement](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/) and the [complete release documentation](https://aspire.dev/whats-new/aspire-13-6/) establish what shipped.
- [David Fowler's developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) provides the broader argument for turning undocumented setup knowledge into explicit operations.
- [David Pine's weather-map post](https://bsky.app/profile/davidpine.dev/post/3mwmut6556k2a) points to a concrete non-.NET application rather than a language-support checklist.
- [Mitch Denny's terminal deep dive](https://devblogs.microsoft.com/aspire/aspire-terminal-support/) and [James Newton-King's Native AOT dashboard article](https://devblogs.microsoft.com/aspire/aspire-dashboard-native-aot/) explain the engineering behind the new experiences.
- [James Newton-King's persistence deep dive](https://devblogs.microsoft.com/aspire/aspire-dashboard-persistence/), published October 8, explains the SQLite and Dapper design behind part one's retained runs and lower-memory telemetry queries.
