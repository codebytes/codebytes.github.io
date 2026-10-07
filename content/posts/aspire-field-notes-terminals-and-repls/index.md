---
title: "Put the Debugging Tools Next to the App"
date: "2026-10-06"
draft: true
categories:
  - "Development"
tags:
  - "Aspire"
  - "Debugging"
  - "PostgreSQL"
  - "CLI"
  - "Testing"
series:
  - "Aspire Field Notes"
series_order: 3
permalink: "/posts/aspire-field-notes-terminals-and-repls/"
slug: "aspire-field-notes-terminals-and-repls"
image: "featured.png"
featureImage: "featured.png"
header:
  teaser: "featured.png"
  og_image: "featured.png"
excerpt_separator: "<!--more-->"
description: "Use Aspire 13.6's terminal dock and database REPLs, distinguish their lifetimes, and automate a resource terminal without mistaking a successful tape for a successful application."
---

The API can connect to the database, but you still need to answer a small question: which database did it actually reach?

That often means finding a port, installing a client, and copying credentials from one place to another. Aspire 13.6 brings that diagnostic interaction next to the resource. The interesting part is not another terminal window. It is the resource context around it.

<!--more-->

This is part three of [Aspire Field Notes](/series/aspire-field-notes/). The terminal APIs and tape workflow discussed here are experimental. Keep them in a deliberate development workflow rather than assuming they are a production administration interface.

The [terminal companion exercise](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/exercises/03-terminals-and-repls) contains the catalog's opt-in PostgreSQL REPL workflow and a separate terminal AppHost. Use that guide to run the checked-in projects; the sections below explain the permissions, lifecycle, and output checks involved.

## Three surfaces with different jobs

Mitch Denny's [terminal deep dive](https://devblogs.microsoft.com/aspire/aspire-terminal-support/) introduces these surfaces. The boundaries below come from the [13.6 release documentation](https://aspire.dev/whats-new/aspire-13-6/#apphost-terminals-and-automation):

| Surface                                | Purpose                                           | Important boundary                                      |
| -------------------------------------- | ------------------------------------------------- | ------------------------------------------------------- |
| Console logs                           | Read stdout and stderr                            | Not a fully interactive terminal                        |
| Resource terminal via `WithTerminal()` | Interact with a terminal-enabled process          | Terminal input reaches that live process                |
| AppHost-owned terminal dock            | Run tools and resource REPLs beside the dashboard | Closing the viewer is not necessarily stopping the tool |

Resource terminals started in 13.5. Aspire 13.6 adds the docked workflows and opt-in database/cache REPLs. That history matters when a sample uses one API but expects another surface's behavior.

## Inspect PostgreSQL without moving its password

The catalog AppHost from [part two](/posts/aspire-field-notes-model-the-whole-app/) already contains the opt-in guard:

```csharp
if (builder.ExecutionContext.IsRunMode && builder.Configuration.GetValue<bool>("Diagnostics:EnableRepl"))
{
    postgres.WithRepl();
}
```

It applies `WithRepl()` to the `postgres` server, not the `catalogdb` database. After the collection setup, stop any catalog run you started, then run these commands from the sample checkout's `aspire-field-notes/` directory:

```bash
apphost=catalog/Catalog.AppHost/Catalog.AppHost.csproj
Diagnostics__EnableRepl=true bash scripts/aspire.sh start \
  --apphost "$apphost" --isolated --non-interactive &&
bash scripts/aspire.sh wait api --apphost "$apphost" \
  --status healthy --timeout 120 --non-interactive &&
bash scripts/aspire.sh resource postgres repl --apphost "$apphost" --non-interactive
```

You can also use **postgres > Actions > REPL** in the dashboard. Either path opens the `psql` client bundled in the container in the dashboard's terminal dock, authenticated using the resource's credentials. The CLI command reports that the command ran; it does not attach your shell, so switch to the dashboard to use the session. You do not need a separately installed PostgreSQL client.[^postgres]

The session initially connects to the `postgres` database. Switch to the application's database explicitly:

```text
\connect catalogdb
```

Then make a small, read-only observation:

```sql
BEGIN READ ONLY;

SELECT current_database(), current_user;

SELECT sku, name, price FROM catalog_items ORDER BY sku;
SELECT count(*) AS products FROM catalog_items;

ROLLBACK;
```

Expect `catalogdb` and three seeded products. These queries use the sample's real `catalog_items` table rather than a hypothetical schema.

The read-only transaction limits this example's queries. It does **not** make the REPL a read-only security boundary: the same credentials may be able to modify or delete data in another transaction.

Exit `psql` with `\q` before closing the tab. Closing the tab alone can leave the client process alive inside the container. Running both the CLI command and the menu action opens two separate sessions, and each needs its own `\q`.

## A useful shortcut is also a permission

REPL support is opt-in and local-run-only. It is available for PostgreSQL, MySQL, SQL Server, MongoDB, Redis, and Valkey in 13.6.[^release]

Enable it only for people you intend to give the resource's actual access. A remotely shared dashboard or tunnel changes who can reach the interface; it does not make the database client harmless.

For repeated team operations, a narrowly defined resource command can be a better interface than an unrestricted prompt. A command named `show-schema-version` communicates a different contract from "here is a shell." Its implementation still needs proper authorization and failure reporting.

## A separate terminal experiment you can repeat

A REPL dock is useful for investigation. A resource terminal is useful when you need to drive an interactive program predictably.

The checked-in [`Terminal.AppHost`](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/terminals/Terminal.AppHost) is a separate SDK-style project. It requires the collection's .NET/Aspire tooling and Node.js, but no PostgreSQL or container runtime. Its application code is:

```csharp
var builder = DistributedApplication.CreateBuilder(args);

#pragma warning disable ASPIRETERMINAL001 // Resource terminals are experimental in 13.6.
builder.AddExecutable("node-repl", "node", ".", "--interactive")
    .WithEnvironment("NODE_REPL_HISTORY", "")
    .WithTerminal(options =>
    {
        options.Columns = 160;
        options.Rows = 30;
    });
#pragma warning restore ASPIRETERMINAL001

builder.Build().Run();
```

The scoped warning suppression marks a real experimental API. It is not a recommendation to disable warnings across an application. The empty `NODE_REPL_HISTORY` setting prevents this exercise from writing personal REPL history.

Start the experiment and inspect its terminal:

```bash
terminal_apphost=terminals/Terminal.AppHost/Terminal.AppHost.csproj
bash scripts/aspire.sh start --apphost "$terminal_apphost" --isolated --non-interactive &&
bash scripts/aspire.sh wait node-repl --apphost "$terminal_apphost" \
  --status up --timeout 90 --non-interactive &&
bash scripts/aspire.sh terminal ps --apphost "$terminal_apphost" --non-interactive
```

Begin from a fresh, idle Node prompt. Coordinate with anyone else viewing that terminal, because input and terminal size are shared. Attaching from a very small window can shrink the terminal enough to break the output check; restart `node-repl` if that happens.

## Automate output, not a fixed sleep

The companion's [`node-smoke.tape`](https://github.com/codebytes/blog-samples/blob/codebytes-aspire-companion-samples/aspire-field-notes/terminals/node-smoke.tape) is a template:

```text
# Use scripts/terminal-smoke.mjs to replace RUN_NONCE with a fresh nonce per run.
Set WaitTimeout 5s
Set TypingSpeed 1ms
Wait+Line /> *$/
Type "console.log(['FIELD','NOTES',6*7,'RUN_NONCE'].join('_'))"
Enter
Wait+Screen@5s /FIELD_NOTES_42_RUN_NONCE/
```

Use the helper rather than playing the template literally. It substitutes a fresh nonce, writes an ignored tape under `artifacts/terminals`, and plays it against `node-repl`:

```bash
node scripts/terminal-smoke.mjs
node scripts/terminal-smoke.mjs
node scripts/terminal-smoke.mjs --negative-control
```

The first two runs must pass with different markers. The typed JavaScript computes `6*7` and joins separate pieces, so input echo cannot contain the full `FIELD_NOTES_42_<nonce>` result. The helper also checks that the final screen contains that computed marker.

`Wait+Screen` can match text left from an earlier attempt. A new nonce prevents the previous run's output from satisfying this run's assertion. `RUN_NONCE` is substituted by the helper, not by Aspire; do not reuse a generated nonce as a repeatability check.

The helper uses five-second output waits, a 20-second playback deadline, and a 35-second outer process deadline. It saves the generated tape, final screen, and diagnostics. A missing prompt or wrong result therefore becomes a bounded failure.[^tapes]

The third command is a deliberate negative control. It generates a fresh tape that computes `6*8` while still waiting for 42, without editing the checked-in template. The helper reports a passing negative control only when the CLI exits with code 16, the screen actually contains the computed 48, and the expected-42 marker is absent. A missing prompt or broken connection cannot masquerade as that successful negative test.

## Know what a tape can and cannot target

Tape playback attaches to a resource configured with `WithTerminal()`. It does not create a shell, take exclusive input ownership, or stop the process after playback.

It also **cannot target a `WithRepl()` client in the AppHost-owned dock**. The PostgreSQL workflow above and the Node terminal experiment are intentionally separate. A terminal-looking interface is not enough to make them interchangeable.

An exit code of zero means the tape completed. It does not prove that every program it typed into a shell succeeded. This companion additionally asserts the fresh computed value; for a business application, also verify an API response, state transition, or another independent result.

After this separate experiment, stop its AppHost explicitly:

```bash
bash scripts/aspire.sh stop \
  --apphost terminals/Terminal.AppHost/Terminal.AppHost.csproj --non-interactive
```

If you also started the catalog for the REPL exercise, stop that AppHost using the collection's scoped cleanup command. Do not use broad process-name cleanup on a machine where other applications may be running.

## Text recordings, not release-demo videos

The tape command writes the final screen to stdout. The supported `Output` directive can record per-command text screens to a new `.txt` or `.ascii` destination.

That is not a video recorder. Video, GIF, image, and asciicast output are not exposed by this Aspire command. A library underneath Aspire supporting a format does not mean the CLI supports it too.[^tapes]

Keep recordings free of secrets. Hiding input from a recording is not the same as preventing it from reaching the process, and a later screen can display what the input caused.

## The result to aim for

Use a REPL to answer a narrow diagnostic question. Use a resource terminal when a program truly needs interactive input. Use a tape when that interaction should be repeatable, and pair it with an independent result check.

The win is less context switching and less undocumented procedure, not giving every tool an unrestricted terminal.

[Next: give a coding agent the same evidence-driven loop](/posts/aspire-field-notes-agents-with-evidence/).

[^release]: [Aspire 13.6 terminal and REPL additions](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/).

[^postgres]: [PostgreSQL REPL authentication, initial database, and lifecycle](https://aspire.dev/integrations/databases/postgres/postgres-host/#open-an-interactive-repl).

[^tapes]: [Terminal tape workflow and supported syntax](https://aspire.dev/dashboard/terminal-tape-playback/) and [command reference, targeting, and exit codes](https://aspire.dev/reference/cli/commands/aspire-terminal-tape-play/).
