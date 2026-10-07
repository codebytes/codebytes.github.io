---
title: "Give Your Coding Agent a Developer Loop, Not a Guess"
date: "2026-10-06"
draft: true
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
header:
  teaser: ""
  og_image: ""
excerpt_separator: "<!--more-->"
description: "Use Aspire 13.6's skills-first setup, scoped lifecycle commands, and runtime evidence to give coding agents a repeatable development workflow."
---

An agent can make a plausible code change without ever running the request that was broken. A successful build will not tell it that it selected the wrong AppHost, queried yesterday's service instance, or restarted a process without rebuilding the changed code.

The improvement I want is not a more confident answer. It is a developer loop that makes those mistakes visible.

<!--more-->

This is part four of [Aspire Field Notes](/series/aspire-field-notes/). We have a model of the application, diagnostic evidence, and resource-level tools. Now we can give an agent the same path a developer would follow.

## Instructions are not observations

Aspire skills teach an agent how to use the tools. They do not start services, instrument applications, or prove that a fix worked.

The runtime tools provide observations and operations: which resources exist, what is healthy, what the logs contain, and which commands a resource exposes. An agent needs both guidance and evidence.

This builds on the distinction in my [skills and plugins guide](/posts/agent-skills-plugins-marketplace/) rather than repeating how to author a `SKILL.md`. David Fowler's [developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) gives a useful architectural explanation: humans, scripts, and agents should operate the same explicit application model.

## Configure the current workflow, not the historical one

In Aspire 13.6, `aspire agent init` installs selected workflow skills. MCP configuration is an **explicit opt-in**, not a prerequisite for using the CLI.[^skills]

For a repository intentionally adopting the standard skill location, the documented workflow skills can be selected explicitly:

```bash
aspire agent init --skill-locations standard \
  --skills aspire,aspire-init,aspire-orchestration,aspire-monitoring,aspire-deployment,aspire-project-v2-migration,aspireify \
  --non-interactive
```

Run setup deliberately and review its file changes. Re-running it with different selections can remove skills from deselected locations. The top-level `aspire` skill routes to the others; installing only that router leaves the guidance incomplete.

If the chosen agent environment needs MCP, opt into it with `--mcp`. Do not copy the old dashboard transport and `aspire mcp init` configuration from the February article and assume it describes 13.6.

Installing a migration skill also does not authorize or execute a migration. The Project V2 skill proposes changes for review after the AppHost has been upgraded.

## First, select the right application

Multiple worktrees and multiple AppHosts make implicit discovery convenient for humans and risky for unattended scripts.

The following Bash sequence assumes a dedicated local worktree, an AppHost at `./AppHost/AppHost.csproj`, and the catalog API resource named `api`. The chained commands stop before inspection if startup or the readiness wait fails:

```bash
aspire start --apphost ./AppHost/AppHost.csproj \
  --isolated --format Json --non-interactive &&
aspire wait api --apphost ./AppHost/AppHost.csproj \
  --status healthy --timeout 90 --non-interactive &&
aspire describe api --apphost ./AppHost/AppHost.csproj \
  --format Json --non-interactive
```

`--isolated` randomizes ports and isolates user secrets. It is not a guarantee that a hard-coded bind mount, named database, or external cloud dependency is isolated. Review those shared surfaces separately, and provide the credentials needed by the isolated development instance through the appropriate store.

The VS Code extension's 13.6 lifecycle work also scopes operations to the current worktree. If the extension owns the running app, use its lifecycle tools rather than casually starting a competing instance.[^release]

## Wait for a fact you actually care about

`aspire start` waits for the AppHost to reach its startup state. That is different from waiting for a particular dependency to serve a request.

`aspire wait api --status healthy` is stronger only when `api` has a meaningful health check. Without one, a running resource can satisfy the `healthy` target. In [part two](/posts/aspire-field-notes-model-the-whole-app/), we added an HTTP check to an endpoint the API implements.

In 13.6, a resource entering `FailedToStart` makes `aspire wait` fail with exit code 18, including when the target was `down`. That prevents a failed startup from being mistaken for a successful stop.[^wait]

Do not work around this with a longer sleep. A missing secret, invalid port, or compilation failure is not slow readiness.

## Ask for a bounded investigation

A useful agent task identifies an operation, the allowed scope, and the result to verify. For example:

```text
Investigate the failing catalog lookup in this worktree.
Use the AppHost at ./AppHost/AppHost.csproj.

Inspect the api resource and the request's logs and trace before editing.
Reproduce the failure using local test data.
Make the smallest change that addresses the observed cause.
Repeat the same request and report the result with its trace evidence.

Do not deploy, reset databases, delete volumes, reveal credentials,
or change dependencies without a separate decision.
If the evidence is missing, say what is missing instead of guessing.
```

The particular wording is less important than the contract. "Fix the app" is not a reproduction procedure.

Query a narrow set of relevant traces rather than handing the agent an entire telemetry database:

```bash
aspire otel traces api --limit 5 --has-error true \
  --apphost ./AppHost/AppHost.csproj --non-interactive
```

Historical comparisons still need a deliberate choice of evidence. Pin the earlier run as described in [part one](/posts/aspire-field-notes-keep-the-failing-run/); do not assume the current CLI query represents the browser's selected historical run.

## Rebuild and restart are different operations

This distinction becomes especially important with the prerelease `Aspire.Hosting.Dotnet` project experience in 13.6.

`AddDotnetProject` can coordinate compatible projects into shared restore/build groups. A resource's **Start** and **Restart** reuse coordinated output; **Rebuild** is the operation to use after changing its source.[^projects]

Discover the selected resource's commands before relying on one:

```bash
aspire resource api --help --apphost ./AppHost/AppHost.csproj
```

If `rebuild` is exposed, use it for that resource's code change and wait for readiness again. If the AppHost model changed, restart the AppHost through its owning lifecycle tool. Frontend HMR and framework-specific hot reload remain separate mechanisms.

Do not replace every stable `AddProject` call just to use the rest of 13.6. Project V2 is prerelease, and custom integrations tied to `ProjectResource` or unsupported resource types require assessment.

### A migration detail worth testing

Coordinated restore does not invoke each root project's `Restore` target independently. Custom `BeforeTargets="Restore"` and `AfterTargets="Restore"` hooks can therefore need attention.

For an AppHost that depends on those hooks, the documented opt-in belongs in the **AppHost's** configuration:

```json
{
  "Aspire": {
    "Dotnet": {
      "RestoreProjectsIndividually": true
    }
  }
}
```

Putting this value in the API resource's runtime environment does not configure the AppHost's build plan. This is the kind of behavior an agent should investigate rather than "fix" by repeatedly restarting.

The .NET 11 multithreaded build optimization is applied only with a sufficiently new selected SDK. It is not a reason to claim that every service in an Aspire 13.6 application must target .NET 11.

## Define completion with evidence

A useful handoff should separate these observations:

| Observation                              | What it establishes                              |
| ---------------------------------------- | ------------------------------------------------ |
| Build completed                          | The selected source compiles in that environment |
| Resource reached readiness               | The configured readiness condition passed        |
| Original request succeeded               | The actual operation was exercised               |
| Expected downstream behavior occurred    | The change did not merely hide a failure         |
| Remaining checks or evidence are missing | The limits of the conclusion                     |

For a flaky failure, one passing request is weak evidence. Repeat the relevant scenario and report the sample size rather than declaring the entire application fixed.

## Keep authority smaller than capability

The agent might be able to run a resource command, open a terminal, or read environment values. That does not mean every such operation is appropriate for the investigation.

Aspire 13.6 improves redaction in `describe`, but secrets embedded in larger connection strings are not automatically detected. Masking also does not sanitize the persisted dashboard database. Keep diagnostic access narrow and review output before sharing it externally.

Do not give an agent a destructive cleanup operation as its default recovery strategy. Explicit resource selection, bounded waits, and clear failures are more useful than clearing all state until something starts.

The goal is an agent that can explain what it observed and what changed, not one that simply has more tools.

[Next: keep state and configuration predictable across environments](/posts/aspire-field-notes-portable-state-and-config/).

[^skills]: [Aspire skills](https://aspire.dev/get-started/aspire-skills/) and [`aspire agent init` selection, removal, and MCP behavior](https://aspire.dev/reference/cli/commands/aspire-agent-init/).

[^release]: [Aspire 13.6 CLI and VS Code changes](https://aspire.dev/whats-new/aspire-13-6/).

[^wait]: [`aspire start` scoping and isolation](https://aspire.dev/reference/cli/commands/aspire-start/) and [`aspire wait` conditions and exit codes](https://aspire.dev/reference/cli/commands/aspire-wait/).

[^projects]: [Project resources, coordinated builds, restore hooks, and migration](https://aspire.dev/integrations/dotnet/project-resources/).
