---
title: "Give Your Coding Agent a Developer Loop, Not a Guess"
draft: true
date: "2026-10-07T09:03:00-04:00"
lastmod: "2026-10-08T23:04:45-04:00"
categories:
  - "Development"
tags:
  - "Aspire"
  - "AI"
  - "GitHub Copilot"
  - "Agent Skills"
  - "Debugging"
series:
  - "Aspire Field Notes"
series_order: 4
permalink: "/posts/aspire-field-notes-agents-with-evidence/"
slug: "aspire-field-notes-agents-with-evidence"
image: "featured.png"
featureImage: "featured.png"
header:
  teaser: "featured.png"
  og_image: "featured.png"
excerpt_separator: "<!--more-->"
description: "Give an agent one failing catalog request to investigate. Scope it to the right AppHost, collect the trace, and require a diagnosis before changing code."
---

An agent can make a plausible code change and get a clean build without ever running the request that was broken. It might have selected the wrong AppHost, queried an old service instance, or restarted without rebuilding.

Before I trust the change, I want to see the request it ran and what happened downstream.

<!--more-->

The earlier [Field Notes](/series/aspire-field-notes/) posts gave us a failing request, its trace, and commands to inspect the app. An agent can use those same tools. David Fowler's [developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) makes that case: humans, scripts, and agents should work from the same application model.

## First, select the right application

With multiple worktrees or AppHosts, implicit discovery can select an application other than the one you're investigating.

Our investigation uses the same catalog app as part one, with the intentional inventory fault enabled. The operation is `GET /api/catalog`. Each Aspire runtime command explicitly selects `--apphost catalog/Catalog.AppHost/Catalog.AppHost.csproj`. We start with `--isolated`, wait for readiness, take an inventory with `aspire describe`, and only then run **Load catalog**, which is expected to fail with the 503. Use a dedicated local worktree, and stop any previous catalog run you started first.

[Walkthrough 04](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/04-agents-with-evidence) has the commands. It works with an existing CLI setup; [installing agent guidance](#optional-install-aspire-guidance) is optional.

In CLI 13.6, `ps` lists AppHosts; `describe --apphost ...` is the resource inventory. Inspect the `api` and `inventory` entries in that result rather than treating an AppHost listing as proof that its services are healthy.

Use the table form here. The JSON form includes environment values, and the API's `ConnectionStrings__catalogdb` and `CATALOGDB_URI` variables embed the database password. `describe` redacts secret variables, but it does not detect a secret inside a larger connection string.

`--isolated` randomizes ports and isolates user secrets. It is not a guarantee that a hard-coded bind mount, named database, or external cloud dependency is isolated. Review those shared surfaces separately, and provide the credentials needed by the isolated development instance through the appropriate store.

The VS Code extension's 13.6 lifecycle work also scopes operations to the current worktree. If the extension owns the running app, use its lifecycle tools rather than casually starting a competing instance.[^release]

## Wait for the API's health check

`aspire start` waits for the AppHost to reach its startup state. That is different from waiting for a particular dependency to serve a request.

`aspire wait api --status healthy` is stronger only when `api` has a meaningful health check. Without one, a running resource can satisfy the `healthy` target. In [part two](/posts/aspire-field-notes-model-the-whole-app/), we added an HTTP check to an endpoint the API implements.

In 13.6, a resource entering `FailedToStart` makes `aspire wait` fail with exit code 18, including when the target was `down`. That prevents a failed startup from being mistaken for a successful stop.[^wait]

Do not work around this with a longer sleep. A missing secret, invalid port, or compilation failure is not slow readiness.

## Ask for a bounded investigation

A useful agent task identifies an operation, the allowed scope, and the result to verify. For example:

```text
Investigate the failing catalog lookup in this worktree.
Use catalog/Catalog.AppHost/Catalog.AppHost.csproj.
The request is GET /api/catalog through the web resource.

Inspect api, inventory, and the request's logs and trace.
Run aspire resource web load-catalog with --apphost set to that project.
Report its HTTP status and trace ID.
Determine whether Inventory__FaultEnabled intentionally selects the failure.
Identify which server first returned 503 and show the parent-child span chain.
Stop after the evidence report.

Do not disable the fault, add retries, fake success, weaken assertions,
deploy, reset databases, delete volumes, or reveal credentials.
If the evidence is missing, say what is missing instead of guessing.
```

This gives the agent a request, a set of resources to inspect, and a stopping point. "Fix the app" leaves all three unspecified.

Here, the correct diagnosis is that the development fault is enabled. Returning a 200, removing a check, or adding retries would hide the behavior we asked the agent to explain.

The readiness wait and the failing command together show healthy resources alongside a failed business operation, and the trace shows that the API-to-inventory call is real. An agent connected through Aspire's MCP server can run the same command with its `execute_resource_command` tool. Follow part one's separate recovery sequence when you intentionally want to turn off the fault.

Query a narrow set of relevant traces rather than handing the agent an entire telemetry database. `aspire otel traces --has-error` returns the failing requests. The dashboard's **Traces** page shows the same evidence, with the errored spans marked:

{{< figure src="failed-traces.png" alt="Aspire dashboard Traces page with two failed api GET /api/catalog traces, each spanning api, catalogdb, and inventory, with error markers on api and inventory" caption="The failed catalog requests include the API, database query, and inventory call. Inspect a trace to find where the 503 began." figureClass="full-width" >}}

Historical comparisons still need a deliberate choice of evidence. Pin the earlier run as described in [part one](/posts/aspire-field-notes-keep-the-failing-run/); do not assume the current CLI query represents the browser's selected historical run.

## Rebuild after a code change

Once an investigation leads to a code change, check how that resource picks it up. Restarting a process doesn't necessarily recompile it.

Discover the selected resource's commands before relying on one. `aspire resource api --help` lists them, and so does the resource's **Actions** menu in the dashboard:

{{< figure src="api-actions-menu.png" alt="Actions menu for the api resource in the Aspire dashboard, listing View details, Console logs, View JSON, Export .env, Structured logs, Traces, Metrics, Stop, Restart, and Rebuild" caption="Rebuild and Restart are separate commands on the catalog API." figureClass="full-width" >}}

In the companion, even the stable `AddProject` API lists `rebuild`, `restart`, and `stop`, and `restart` states that source code is not recompiled. Use `rebuild` after changing a resource's code, then wait for readiness again. If the AppHost model changed, restart the AppHost through its owning lifecycle tool. Frontend HMR and framework-specific hot reload remain separate mechanisms.

## What the handoff should contain

A useful handoff should separate these observations:

| Observation                              | What it establishes                                                    |
| ---------------------------------------- | ---------------------------------------------------------------------- |
| Build completed                          | The selected source compiles in that environment                       |
| Resource reached readiness               | The configured readiness condition passed                              |
| Expected request result was observed     | The actual operation matched the healthy or intentionally failing case |
| Expected downstream behavior occurred    | The change did not merely hide a failure                               |
| Remaining checks or evidence are missing | The limits of the conclusion                                           |

For this investigation, the handoff should identify the enabled fault, the inventory span that returned 503, and the API span that passed it back. A 503 is the expected result. For a real intermittent bug, repeat the scenario and report how many attempts passed or failed.

After stopping the sample's AppHosts, run `bash scripts/check.sh` for the build and regression checks. Keep those results alongside the request-level findings.

## Optional: install Aspire guidance

Aspire skills teach an agent how to use the tools; runtime commands give it observations about the app. My [skills and plugins guide](/posts/agent-skills-plugins-marketplace/) covers the distinction in more detail.

In Aspire 13.6, `aspire agent init` installs selected workflow skills. MCP configuration is an **explicit opt-in**, not a prerequisite for using the CLI.[^skills] Skip setup if your agent already has the guidance it needs.

Before running it, account for changes outside the project. CLI 13.6 registers a `PostToolUse` telemetry hook in the user-level configuration of detected GitHub Copilot and Claude Code clients, and copies hook scripts into your Aspire home directory (`~/.aspire` by default). This happens even when skill files go into a project directory. `ASPIRE_CLI_TELEMETRY_OPTOUT=true` suppresses transmission while set, but does not prevent hook registration. Setting it for one command does not disable later hook executions.[^setup-scope]

Walkthrough 04 shows a command that targets the catalog workspace, writes GitHub-compatible skills to `catalog/.github/skills`, names the workflow skills, and passes `--mcp=false`. There are a few details to review:

- The `github` location scopes the skill files only. In 13.6, `standard` also targets user-level `~/.agents/skills`.
- `--mcp=false` skips new MCP configuration but does not remove an existing connection. Setup can still rewrite deprecated workspace entries from `aspire mcp start` to `aspire agent mcp`.
- `--skills all` can include optional companion-tool installation. Select the workflow skills you need; the top-level `aspire` router alone leaves the guidance incomplete.
- Deselection is not reliable cleanup in this version. Although the command reference says deselected locations are removed, the 13.6 implementation, unchanged in 13.6.1, only removes `playwright-cli` folders it created during that same run. Review the files in each location after changing selections.

If your agent needs MCP, opt into it with `--mcp` using the current configuration. The old dashboard transport and `aspire mcp init` setup in my February article don't describe 13.6.

## If you're evaluating Project V2

The companion uses stable `AddProject` resources. The prerelease `Aspire.Hosting.Dotnet` package is a separate migration choice; none of the investigation above requires it.

Its `AddDotnetProject` API can coordinate compatible projects into shared restore/build groups. **Start** and **Restart** reuse coordinated output, while **Rebuild** compiles changed source.[^projects] Check custom integrations tied to `ProjectResource` and unsupported resource types before migrating. Installing the migration skill doesn't perform or authorize that migration; it proposes changes after the AppHost upgrade.

Coordinated restore also skips independent invocation of each root project's `Restore` target. If you depend on `BeforeTargets="Restore"` or `AfterTargets="Restore"` hooks, test them. The documented opt-in belongs in the **AppHost's** configuration:

```json
{
  "Aspire": {
    "Dotnet": {
      "RestoreProjectsIndividually": true
    }
  }
}
```

Putting this in the API's runtime environment won't change the AppHost's build plan. The .NET 11 multithreaded build optimization likewise depends on the selected SDK; it doesn't require every service to target .NET 11.

## Keep diagnostic access narrow

A resource command, terminal, or environment export can expose more than this investigation needs. Connection strings and persisted dashboard data can contain secrets despite UI masking, so review output before sharing it.

Keep destructive cleanup out of the agent's default recovery path. If a request fails, the first useful action is to inspect that request, not clear the database until the app starts.

[Next: keep state and configuration predictable across environments](/posts/aspire-field-notes-portable-state-and-config/).

[^skills]: [Aspire skills](https://aspire.dev/get-started/aspire-skills/) and [`aspire agent init` selection, removal, and MCP behavior](https://aspire.dev/reference/cli/commands/aspire-agent-init/).

[^setup-scope]: The 13.6.1 tagged implementations of [skill locations](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Cli/Agents/SkillLocation.cs) and [agent initialization, including phase 6 hook registration](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Cli/Commands/AgentInitCommand.cs) define the actual setup scope; both files are unchanged from 13.6.0. The [CLI telemetry reference](https://aspire.dev/reference/cli/microsoft-collected-cli-telemetry/#ai-agent-skill-usage) documents the hook.

[^release]: [Aspire 13.6 CLI and VS Code changes](https://aspire.dev/whats-new/aspire-13-6/).

[^wait]: [`aspire start` scoping and isolation](https://aspire.dev/reference/cli/commands/aspire-start/) and [`aspire wait` conditions and exit codes](https://aspire.dev/reference/cli/commands/aspire-wait/).

[^projects]: [Project resources, coordinated builds, restore hooks, and migration](https://aspire.dev/integrations/dotnet/project-resources/).
