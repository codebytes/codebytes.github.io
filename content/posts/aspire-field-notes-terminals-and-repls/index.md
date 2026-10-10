---
title: "Put the Debugging Tools Next to the App"
draft: true
date: "2026-10-07T09:02:00-04:00"
lastmod: "2026-10-08T23:04:45-04:00"
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
description: "Query PostgreSQL from Aspire's terminal dock, then automate a Node REPL with a repeatable output check. The two terminal experiences work differently."
---

The API can connect to the database, but you still need to answer a small question: which database did it actually reach?

That often means finding a port, installing a client, and copying credentials. In Aspire 13.6, you can open a database REPL from the resource's Actions menu with its connection already configured.

<!--more-->

For this part of [Aspire Field Notes](/series/aspire-field-notes/), we'll query the catalog database, then try a separate Node terminal that can be automated. The two look similar in the dashboard, but they have different lifetimes and APIs.

## Three surfaces with different jobs

Mitch Denny's [terminal deep dive](https://devblogs.microsoft.com/aspire/aspire-terminal-support/) introduces these surfaces. The boundaries below come from the [13.6 release documentation](https://aspire.dev/whats-new/aspire-13-6/#apphost-terminals-and-automation):

| Surface                                | Purpose                                           | Important boundary                                      |
| -------------------------------------- | ------------------------------------------------- | ------------------------------------------------------- |
| Console logs                           | Read stdout and stderr                            | Not a fully interactive terminal                        |
| Resource terminal via `WithTerminal()` | Interact with a terminal-enabled process          | Terminal input reaches that live process                |
| AppHost-owned terminal dock            | Run tools and resource REPLs beside the dashboard | Closing the viewer is not necessarily stopping the tool |

Resource terminals started in 13.5. Aspire 13.6 adds the docked workflows and opt-in database/cache REPLs.

## Inspect PostgreSQL without moving its password

The catalog AppHost from [part two](/posts/aspire-field-notes-model-the-whole-app/) already contains the opt-in guard:

```csharp
if (builder.ExecutionContext.IsRunMode && builder.Configuration.GetValue<bool>("Diagnostics:EnableRepl"))
{
    postgres.WithRepl();
}
```

It applies `WithRepl()` to the `postgres` server, not the `catalogdb` database. The [PostgreSQL walkthrough](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/03-terminals-and-repls) has the setup and startup commands.

Start the catalog with `Diagnostics__EnableRepl=true`, then choose **postgres > Actions > REPL** in the dashboard, or run `aspire resource postgres repl`. Either opens the container's bundled `psql` client in the dashboard dock, authenticated with the resource's credentials. The CLI command doesn't attach your shell. Switch to the dashboard; if the dock is hidden, press the backtick (`` ` ``) key.[^postgres]

The session starts in the `postgres` database. Connect to `catalogdb` and inspect the seeded products in a read-only transaction:

```sql
\connect catalogdb
BEGIN READ ONLY;
SELECT
    current_database(),
    current_user;
SELECT sku, name, price
FROM catalog_items
ORDER BY sku;
SELECT count(*) AS products
FROM catalog_items;
ROLLBACK;
\q
```

{{< figure src="psql-repl-dock.png" alt="Aspire dashboard with the psql (postgres) terminal docked below the resources: it connects to catalogdb, begins a read-only transaction, and lists the mug, notebook, and sticker from catalog_items" caption="The docked client connects to catalogdb and returns the three seeded products from catalog_items." figureClass="full-width" >}}

The read-only transaction limits this example's queries. It does **not** make the REPL a read-only security boundary: the same credentials may be able to modify or delete data in another transaction.

The final `\q` matters: closing the tab alone can leave `psql` alive inside the container. Running both the CLI command and the menu action opens two sessions, and each needs its own `\q`.

## A useful shortcut is also a permission

REPL support is opt-in and local-run-only. It is available for PostgreSQL, MySQL, SQL Server, MongoDB, Redis, and Valkey in 13.6.[^release]

Enable it only for people you intend to give the resource's actual access. A remotely shared dashboard or tunnel changes who can reach the interface; it does not make the database client harmless.

For a repeated team operation, consider a resource command such as `show-schema-version` instead of a full database prompt. Its implementation still needs authorization and clear failure reporting.

## A separate terminal experiment you can repeat

A REPL dock is useful for investigation. A resource terminal is useful when you need to drive an interactive program predictably.

The checked-in [`Terminal.AppHost`](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/terminals/Terminal.AppHost) is a separate SDK-style project. It requires the collection's .NET/Aspire tooling and Node.js, but no PostgreSQL or container runtime. Its application code is:

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

`WithTerminal()` is experimental in 13.6, so the warning suppression is scoped to that call. The empty `NODE_REPL_HISTORY` setting keeps this experiment out of your personal Node REPL history.

Start the Terminal AppHost and open `node-repl`'s **Console logs** page. For a resource with `WithTerminal()`, that page is the interactive terminal, sized 160x30 by the options above. `aspire terminal ps` lists the same session from a terminal.

Begin from a fresh, idle Node prompt. Coordinate with anyone else viewing that terminal, because input and terminal size are shared. By default, `terminal attach` takes the primary role and resizes the terminal to your window, so attaching from a very small window can shrink it enough to break the output check. Restarting only `node-repl` can keep the reduced size. Attach again from a normal-size window and detach with **Ctrl+B D**, or stop and start the Terminal AppHost. Pass `--viewer` when you only want to watch.[^attach]

## Automate output, not a fixed sleep

The companion's [`node-smoke.tape`](https://github.com/codebytes/blog-samples/blob/main/aspire-field-notes/terminals/node-smoke.tape) is a template:

```text
# Use scripts/terminal-smoke.mjs to replace RUN_NONCE with a fresh nonce per run.
Set WaitTimeout 5s
Set TypingSpeed 1ms
Wait+Line /> *$/
Type "console.log(['FIELD','NOTES',6*7,'RUN_NONCE'].join('_'))"
Enter
Wait+Screen@5s /FIELD_NOTES_42_RUN_NONCE/
```

The companion's `terminal-smoke.mjs` helper fills in a fresh nonce, writes the tape, and plays it against `node-repl` with `aspire terminal tape play`. The dashboard terminal shows the line the tape typed and the result Node computed:

{{< figure src="node-repl-terminal.png" alt="The node-repl terminal in the Aspire dashboard after tape playback: the typed console.log line and its output, FIELD_NOTES_42 followed by a fresh nonce" caption="The computed FIELD_NOTES_42 marker appears below the input. A fresh nonce distinguishes it from earlier output." figureClass="full-width" >}}

Each run uses a different marker. The typed JavaScript computes `6*7` and joins separate pieces, so input echo cannot contain the full `FIELD_NOTES_42_<nonce>` result. The helper also checks that the final screen contains that computed marker.

`Wait+Screen` can match text left from an earlier attempt. A new nonce prevents the previous run's output from satisfying this run's assertion. `RUN_NONCE` is substituted by the helper, not by Aspire; do not reuse a generated nonce as a repeatability check.

The helper uses five-second output waits, a 20-second playback deadline, and a 35-second outer process deadline. If it can't find the prompt or result, it fails within those limits and saves the tape, final screen, and diagnostics.[^tapes]

To check that the assertion can fail, run the helper with `--negative-control`. It computes `6*8` while still waiting for 42, without editing the checked-in template. The helper accepts this as a successful negative test only if the CLI exits with code 16, the screen contains the computed 48, and the expected-42 marker is absent. A broken connection won't satisfy those checks.

## Know what a tape can and cannot target

Tape playback attaches to a resource configured with `WithTerminal()`. It does not create a shell, take exclusive input ownership, or stop the process after playback.

It **cannot target a `WithRepl()` client in the AppHost-owned dock**. That's why the PostgreSQL session and Node experiment are separate.

An exit code of zero means the tape completed. It does not prove that every program it typed into a shell succeeded. This companion additionally asserts the fresh computed value; for a business application, also verify an API response, state transition, or another independent result.

When you finish, stop each AppHost with its own scoped `aspire stop --apphost` command. Do not use broad process-name cleanup on a machine where other applications may be running.

## What a tape recording contains

The tape command writes the final screen to stdout. The supported `Output` directive can record per-command text screens to a new `.txt` or `.ascii` destination.

The Aspire command does not expose video, GIF, image, or asciicast output, even where its underlying library supports those formats.[^tapes]

Keep recordings free of secrets. Hiding input from a recording is not the same as preventing it from reaching the process, and a later screen can display what the input caused.

## Use the smallest tool that answers the question

Use a REPL to answer a narrow diagnostic question. Use a resource terminal when a program truly needs interactive input. Use a tape when that interaction should be repeatable, and pair it with an independent result check.

For the catalog question, a short SQL query is enough. The tape becomes useful when the interaction itself needs to be repeated.

[Walkthrough 03](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/03-terminals-and-repls) has the setup and exact commands for both experiments: the catalog's opt-in PostgreSQL REPL and the separate Node terminal AppHost.

[Next: give a coding agent the same evidence-driven loop](/posts/aspire-field-notes-agents-with-evidence/).

[^release]: [Aspire 13.6 terminal and REPL additions](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/).

[^postgres]: [PostgreSQL REPL authentication, initial database, and lifecycle](https://aspire.dev/integrations/databases/postgres/postgres-host/#open-an-interactive-repl).

[^attach]: [`aspire terminal attach` roles, hotkeys, and viewer mode](https://aspire.dev/reference/cli/commands/aspire-terminal-attach/).

[^tapes]: [Terminal tape workflow and supported syntax](https://aspire.dev/dashboard/terminal-tape-playback/) and [command reference, targeting, and exit codes](https://aspire.dev/reference/cli/commands/aspire-terminal-tape-play/).
