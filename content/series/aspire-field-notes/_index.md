---
title: "Aspire Field Notes: A Better Developer Loop"
description: "Six practical workflows for Aspire 13.6: preserve evidence, model the application, inspect dependencies, guide agents, move configuration, and choose a deployment."
draft: true
---

A working demo answers one question: can the application start? A useful developer loop answers the next ones. What failed? Can someone else reproduce it? Does the fix change the right thing? What happens when this leaves my laptop?

**Aspire Field Notes** follows those questions through Aspire 13.6. This is not another installation guide or an inventory of every release-note bullet. Each post starts with a development problem, uses a specific capability to address it, and finishes with an observable result.

## The reading path

| Part | Post                                                                                                         | What you will do                                                                                                   |
| ---- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| 1    | [Stop Losing the Bug When You Restart Aspire](/posts/aspire-field-notes-keep-the-failing-run/)               | Preserve a failure, compare diagnostic runs, and understand what the dashboard actually retains                    |
| 2    | [A Polyglot App Is More Than a Process List](/posts/aspire-field-notes-model-the-whole-app/)                 | Connect configuration, readiness, and telemetry across languages, including the new Java and Rust hosting previews |
| 3    | [Put the Debugging Tools Next to the App](/posts/aspire-field-notes-terminals-and-repls/)                    | Inspect a database through the terminal dock and build a bounded, repeatable terminal check                        |
| 4    | [Give Your Coding Agent a Developer Loop, Not a Guess](/posts/aspire-field-notes-agents-with-evidence/)      | Scope an agent to the right AppHost, wait for real readiness, and verify a change with runtime evidence            |
| 5    | [One Configuration Contract, From Laptop to Container](/posts/aspire-field-notes-portable-state-and-config/) | Keep application settings stable while paths, connection names, credentials, and storage change                    |
| 6    | [Same AppHost, Different Deployment Promises](/posts/aspire-field-notes-choose-your-deployment/)             | Choose a deployment target from workload constraints rather than assume every publisher behaves alike              |

Read them in order for the full story, or start with the problem you have today. The terminal experiment in part three can be run independently.

## The application behind the examples

Imagine a small catalog application: a Vite frontend named `web`, an API named `api`, and PostgreSQL holding the catalog. The API might be .NET, an existing service might be Java, and a specialized worker might be Rust or Python. The point is to describe that system, not add languages to make the diagram look impressive.

The AppHost snippets are integration recipes for existing services, not a claim that this blog repository contains a complete catalog application. Each recipe names its prerequisites. For a complete app you can run, the [official Node.js weather-map sample](https://aspire.dev/reference/samples/aspire-with-node/) demonstrates a frontend, instrumented API, and external dependency under a TypeScript AppHost.

The series targets **Aspire 13.6.0**. Preview packages and experimental APIs are identified where they appear. Examples do not require migrating stable `AddProject` resources to the prerelease .NET project model, deploying Azure resources, or giving an agent access to credentials.

## What this builds on

My earlier [CLI introduction](/posts/aspire-cli-getting-started/) and [deployment article](/posts/aspire-cli-part-2/) cover the original command-oriented journey. The [MCP article](/posts/aspire-cli-part-3-mcp/) and [skills, plugins, and marketplace guide](/posts/agent-skills-plugins-marketplace/) explain the agent-tooling background.

Those articles reflect their publication versions. This series uses the 13.6 documentation for current commands and behavior, particularly the move to skills-first agent setup with optional MCP.

Detailed retry-policy design and AI-provider selection deserve their own space. Here, resilience is something to investigate with evidence, and AI is a participant in the developer loop rather than an excuse to repeat a provider comparison.

## Sources worth exploring

- [Maddy Montaquila's 13.6 announcement](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/) and the [complete release documentation](https://aspire.dev/whats-new/aspire-13-6/) establish what shipped.
- [David Fowler's developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) provides the broader argument for turning undocumented setup knowledge into explicit operations.
- [David Pine's weather-map post](https://bsky.app/profile/davidpine.dev/post/3mwmut6556k2a) points to a concrete non-.NET application rather than a language-support checklist.
- [Mitch Denny's terminal deep dive](https://devblogs.microsoft.com/aspire/aspire-terminal-support/) and [James Newton-King's Native AOT dashboard article](https://devblogs.microsoft.com/aspire/aspire-dashboard-native-aot/) explain the engineering behind the new experiences.

All six articles are drafts awaiting review. Publication dates will be chosen separately.
