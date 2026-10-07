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
image: "featured.png"
featureImage: "featured.png"
header:
  teaser: "featured.png"
  og_image: "featured.png"
excerpt_separator: "<!--more-->"
description: "Use Aspire 13.6's skills-first setup, scoped lifecycle commands, and runtime evidence to give coding agents a repeatable development workflow."
---

An agent can make a plausible code change without ever running the request that was broken. A successful build will not tell it that it selected the wrong AppHost, queried yesterday's service instance, or restarted a process without rebuilding the changed code.

The improvement I want is not a more confident answer. It is a developer loop that makes those mistakes visible.

<!--more-->

This is part four of [Aspire Field Notes](/series/aspire-field-notes/). We have a model of the application, diagnostic evidence, and resource-level tools. Now we can give an agent the same path a developer would follow.

The [companion investigation](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/exercises/04-agents-with-evidence) uses the same catalog application as part one. Follow the collection's setup, including `node scripts/init-secret.mjs`, then run the commands below from the sample checkout's `aspire-field-notes/` directory. They call the `aspire` CLI directly and assume version 13.6.1 or later. The business operation to investigate is `GET /api/catalog`, not an invented endpoint.

## Instructions are not observations

Aspire skills teach an agent how to use the tools. They do not start services, instrument applications, or prove that a fix worked.

The runtime tools provide observations and operations: which resources exist, what is healthy, what the logs contain, and which commands a resource exposes. An agent needs both guidance and evidence.

This builds on the distinction in my [skills and plugins guide](/posts/agent-skills-plugins-marketplace/) rather than repeating how to author a `SKILL.md`. David Fowler's [developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) gives a useful architectural explanation: humans, scripts, and agents should operate the same explicit application model.

## Optional: install Aspire guidance

In Aspire 13.6, `aspire agent init` installs selected workflow skills. MCP configuration is an **explicit opt-in**, not a prerequisite for using the CLI.[^skills]

The companion exercises do not require this setup command. Skip it if your agent already has suitable guidance, or if you do not want it to modify your agent configuration.

**This is not a wholly project-local operation.** In CLI 13.6, setup registers a `PostToolUse` telemetry hook in the user-level configuration of detected GitHub Copilot and Claude Code clients, and copies the hook scripts into your Aspire home directory (`~/.aspire` by default). That happens even when the skill files target a project directory. `ASPIRE_CLI_TELEMETRY_OPTOUT=true` suppresses telemetry transmission while it is set; it does not prevent hook registration. The per-command assignment below does not disable telemetry for later hook executions.[^setup-scope]

If you intentionally want that setup, the following command selects the catalog workspace and puts its GitHub-compatible skill files in `catalog/.github/skills`:

```bash
ASPIRE_CLI_TELEMETRY_OPTOUT=true aspire agent init \
  --workspace-root "$PWD/catalog" --skill-locations github \
  --skills aspire,aspire-init,aspireify,aspire-orchestration,aspire-monitoring,aspire-deployment,aspire-project-v2-migration \
  --mcp=false --non-interactive
```

The `github` location scopes the skill files, not all setup side effects. In 13.6, `standard` additionally targets user-level `~/.agents/skills`; it is not a synonym for "only this project." `--mcp=false` skips new MCP server configuration and does not remove an existing MCP connection. Setup can still rewrite deprecated `aspire mcp start` entries it finds in the workspace's MCP configuration files to `aspire agent mcp`.

Name the workflow skills rather than using `--skills all`, which can include optional companion-tool installation. The top-level `aspire` skill routes to the others; installing only that router leaves the guidance incomplete.

Run setup deliberately and review its file changes. Do not rely on a later run to clean up: the command reference says deselected locations are removed, but the 13.6 implementation, unchanged in 13.6.1, only removes `playwright-cli` folders it created during that same run. Review each location's files yourself after changing selections. Other agent hosts may require a different location, but that should be a separate, informed choice rather than an unnoticed change to personal tooling.

If the chosen agent environment needs MCP, opt into it with `--mcp`. Do not copy the old dashboard transport and `aspire mcp init` configuration from the February article and assume it describes 13.6.

Installing a migration skill also does not authorize or execute a migration. The Project V2 skill proposes changes for review after the AppHost has been upgraded.

## First, select the right application

Multiple worktrees and multiple AppHosts make implicit discovery convenient for humans and risky for unattended scripts.

The following Bash sequence selects the companion's catalog AppHost explicitly and enables its intentional inventory fault. Use a dedicated local worktree, stopping any previous catalog run you started first. The chained commands stop if startup, readiness, or the expected-failure assertion fails:

```bash
Inventory__FaultEnabled=true aspire start \
  --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj \
  --isolated --format Json --non-interactive &&
aspire wait api --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj \
  --status healthy --timeout 90 --non-interactive &&
node scripts/smoke.mjs fault &&
aspire describe --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj \
  --format Table --non-interactive
```

In CLI 13.6, `ps` lists AppHosts; `describe --apphost ...` is the resource inventory. Inspect the `api` and `inventory` entries in that result rather than treating an AppHost listing as proof that its services are healthy.

Use the table form here. The JSON form includes environment values, and the API's `ConnectionStrings__catalogdb` and `CATALOGDB_URI` variables embed the database password. `describe` redacts secret variables, but it does not detect a secret inside a larger connection string.

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
Use catalog/Catalog.AppHost/Catalog.AppHost.csproj.
Confirm that aspire --version reports 13.6.1 or later before running Aspire commands.
The request is GET /api/catalog through the web resource.

Inspect api, inventory, and the request's logs and trace.
Run node scripts/smoke.mjs fault and report its trace ID and evidence directory.
Determine whether Inventory__FaultEnabled intentionally selects the failure.
Identify which server first returned 503 and show the parent-child span chain.
Stop after the evidence report.

Do not disable the fault, add retries, fake success, weaken assertions,
deploy, reset databases, delete volumes, or reveal credentials.
If the evidence is missing, say what is missing instead of guessing.
```

The particular wording is less important than the contract. "Fix the app" is not a reproduction procedure.

With a deliberately injected sample failure, the correct diagnosis can be that the development fault is enabled. Do not reward an agent for hiding the 503 behind a success response, removing a check, or adding retries until the exercise looks green. The expected result and the reason for the failure must remain observable.

The fault check proves healthy resources and a failed business operation together. Its artifacts include console logs, structured logs, and spans; the API-to-inventory call is real. Follow part one's separate recovery sequence when you intentionally want to turn off the fault.

Query a narrow set of relevant traces rather than handing the agent an entire telemetry database:

```bash
aspire otel traces api --limit 5 --has-error \
  --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj --non-interactive
```

Historical comparisons still need a deliberate choice of evidence. Pin the earlier run as described in [part one](/posts/aspire-field-notes-keep-the-failing-run/); do not assume the current CLI query represents the browser's selected historical run.

## Rebuild and restart are different operations

This distinction becomes especially important with the prerelease `Aspire.Hosting.Dotnet` project experience in 13.6.

The companion deliberately uses stable `AddProject` resources. The Project V2 discussion below is an optional migration consideration, not a hidden prerequisite or a migration performed by the exercise.

`AddDotnetProject` can coordinate compatible projects into shared restore/build groups. A resource's **Start** and **Restart** reuse coordinated output; **Rebuild** is the operation to use after changing its source.[^projects]

Discover the selected resource's commands before relying on one:

```bash
aspire resource api --help \
  --apphost ./catalog/Catalog.AppHost/Catalog.AppHost.csproj
```

In the companion, even the stable `AddProject` API lists `rebuild`, `restart`, and `stop`, and `restart` states that source code is not recompiled. Use `rebuild` after changing a resource's code, then wait for readiness again. If the AppHost model changed, restart the AppHost through its owning lifecycle tool. Frontend HMR and framework-specific hot reload remain separate mechanisms.

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

| Observation                              | What it establishes                                                    |
| ---------------------------------------- | ---------------------------------------------------------------------- |
| Build completed                          | The selected source compiles in that environment                       |
| Resource reached readiness               | The configured readiness condition passed                              |
| Expected request result was observed     | The actual operation matched the healthy or intentionally failing case |
| Expected downstream behavior occurred    | The change did not merely hide a failure                               |
| Remaining checks or evidence are missing | The limits of the conclusion                                           |

For a flaky failure, one passing request is weak evidence. Repeat the relevant scenario and report the sample size rather than declaring the entire application fixed. For this controlled exercise, use the checked-in assertions rather than changing their expected 503 into 200.

After stopping the sample's AppHosts, run `bash scripts/check.sh` for the build and regression checks. Those checks are useful evidence, but they do not replace the request-level reproduction.

## Keep authority smaller than capability

The agent might be able to run a resource command, open a terminal, or read environment values. That does not mean every such operation is appropriate for the investigation.

Aspire 13.6 improves redaction in `describe`, but secrets embedded in larger connection strings are not automatically detected. Masking also does not sanitize the persisted dashboard database. Keep diagnostic access narrow and review output before sharing it externally.

Do not give an agent a destructive cleanup operation as its default recovery strategy. Explicit resource selection, bounded waits, and clear failures are more useful than clearing all state until something starts.

The goal is an agent that can explain what it observed and what changed, not one that simply has more tools.

[Next: keep state and configuration predictable across environments](/posts/aspire-field-notes-portable-state-and-config/).

[^skills]: [Aspire skills](https://aspire.dev/get-started/aspire-skills/) and [`aspire agent init` selection, removal, and MCP behavior](https://aspire.dev/reference/cli/commands/aspire-agent-init/).

[^setup-scope]: The 13.6.1 tagged implementations of [skill locations](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Cli/Agents/SkillLocation.cs) and [agent initialization, including phase 6 hook registration](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Cli/Commands/AgentInitCommand.cs) define the actual setup scope; both files are unchanged from 13.6.0. The [CLI telemetry reference](https://aspire.dev/reference/cli/microsoft-collected-cli-telemetry/#ai-agent-skill-usage) documents the hook.

[^release]: [Aspire 13.6 CLI and VS Code changes](https://aspire.dev/whats-new/aspire-13-6/).

[^wait]: [`aspire start` scoping and isolation](https://aspire.dev/reference/cli/commands/aspire-start/) and [`aspire wait` conditions and exit codes](https://aspire.dev/reference/cli/commands/aspire-wait/).

[^projects]: [Project resources, coordinated builds, restore hooks, and migration](https://aspire.dev/integrations/dotnet/project-resources/).
