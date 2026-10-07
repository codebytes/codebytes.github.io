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
header:
  teaser: ""
  og_image: ""
excerpt_separator: "<!--more-->"
description: "Use Aspire 13.6's terminal dock and database REPLs, distinguish their lifetimes, and automate a resource terminal without mistaking a successful tape for a successful application."
---

The API can connect to the database, but you still need to answer a small question: which database did it actually reach?

That often means finding a port, installing a client, and copying credentials from one place to another. Aspire 13.6 brings that diagnostic interaction next to the resource. The interesting part is not another terminal window. It is the resource context around it.

<!--more-->

This is part three of [Aspire Field Notes](/series/aspire-field-notes/). The terminal APIs and tape workflow discussed here are experimental. Keep them in a deliberate development workflow rather than assuming they are a production administration interface.

## Three surfaces with different jobs

Mitch Denny's [terminal deep dive](https://devblogs.microsoft.com/aspire/aspire-terminal-support/) shows how the pieces fit together:

| Surface                                | Purpose                                           | Important boundary                                      |
| -------------------------------------- | ------------------------------------------------- | ------------------------------------------------------- |
| Console logs                           | Read stdout and stderr                            | Not a fully interactive terminal                        |
| Resource terminal via `WithTerminal()` | Interact with a terminal-enabled process          | Terminal input reaches that live process                |
| AppHost-owned terminal dock            | Run tools and resource REPLs beside the dashboard | Closing the viewer is not necessarily stopping the tool |

Resource terminals started in 13.5. Aspire 13.6 adds the docked workflows and opt-in database/cache REPLs. That history matters when a sample uses one API but expects another surface's behavior.

## Inspect PostgreSQL without moving its password

For the catalog AppHost from [part two](/posts/aspire-field-notes-model-the-whole-app/), replace the PostgreSQL definition with:

```csharp
var postgres = builder.AddPostgres("postgres").WithRepl();
var database = postgres.AddDatabase("catalogdb");
```

Keep the API's existing reference to `database`. This uses `Aspire.Hosting.PostgreSQL` 13.6.0 and requires the local PostgreSQL container to be running.

The server gets a **REPL** command in the dashboard. It opens the `psql` client bundled in the container, authenticated using the resource's credentials. You do not need a separately installed PostgreSQL client.[^postgres]

The session initially connects to the `postgres` database. Switch to the application's database explicitly:

```text
\connect catalogdb
```

Then make a small, read-only observation:

```sql
BEGIN READ ONLY;

SELECT current_database(), current_user;

SELECT count(*) AS visible_tables
FROM information_schema.tables
WHERE table_schema = 'public';

ROLLBACK;
```

This answers where the session connected and whether it can see tables. It does not depend on an invented `products` schema or create data just to make the demonstration work.

The read-only transaction limits this example's queries. It does **not** make the REPL a read-only security boundary: the same credentials may be able to modify or delete data in another transaction.

Exit `psql` with `\q` before closing the tab. Closing the tab alone can leave the client process alive inside the container.

## A useful shortcut is also a permission

REPL support is opt-in and local-run-only. It is available for PostgreSQL, MySQL, SQL Server, MongoDB, Redis, and Valkey in 13.6.[^release]

Enable it only for people you intend to give the resource's actual access. A remotely shared dashboard or tunnel changes who can reach the interface; it does not make the database client harmless.

For repeated team operations, a narrowly defined resource command can be a better interface than an unrestricted prompt. A command named `show-schema-version` communicates a different contract from "here is a shell." Its implementation still needs proper authorization and failure reporting.

## A separate terminal experiment you can repeat

A REPL dock is useful for investigation. A resource terminal is useful when you need to drive an interactive program predictably.

The following is a complete, separate file-based C# AppHost for a local Node.js REPL. It requires Aspire 13.6 and Node.js on `PATH`; it does not need PostgreSQL or a container runtime. Save it as `apphost.cs` in a scratch project, not over your catalog AppHost:

```csharp
#:sdk Aspire.AppHost.Sdk@13.6.0

var builder = DistributedApplication.CreateBuilder(args);

#pragma warning disable ASPIRETERMINAL001
builder.AddExecutable("probe", "node", ".", "--interactive")
    .WithTerminal();
#pragma warning restore ASPIRETERMINAL001

builder.Build().Run();
```

The scoped warning suppression marks a real experimental API. It is not a recommendation to disable warnings across an application.

Start the experiment and inspect its terminal:

```bash
aspire start --apphost ./apphost.cs --non-interactive
aspire terminal ps --apphost ./apphost.cs --non-interactive
```

Begin from a fresh, idle Node prompt. Coordinate with anyone else viewing that terminal, because input is shared.

## Automate output, not a fixed sleep

Save this as `probe.tape` beside the experimental AppHost:

```text
Set TypingSpeed 0
Set WaitTimeout 10s

Wait+Line /> *$/
Type "console.log('FIELD_NOTES_' + 'READY_13_6')"
Enter
Wait+Screen /FIELD_NOTES_READY_13_6/
Wait+Line /> *$/
```

Play it against the already running resource:

```bash
aspire terminal tape play probe --tape-file probe.tape \
  --apphost ./apphost.cs --timeout 30 --non-interactive
```

The marker is split in the typed JavaScript expression so the input echo does not contain the complete expected output. That avoids passing the wait merely because the terminal echoed what we typed.

There is another trap: `Wait+Screen` can match text left from an earlier attempt. Use a fresh resource or a new marker when repeating this check. A successful wait is evidence that matching text is visible, not proof that the latest command produced it.

The per-wait limit and overall timeout have different jobs. Both should be bounded so a missing prompt becomes an explicit failure instead of an indefinitely occupied developer session.[^tapes]

## Know what a tape can and cannot target

Tape playback attaches to a resource configured with `WithTerminal()`. It does not create a shell, take exclusive input ownership, or stop the process after playback.

It also **cannot target a `WithRepl()` client in the AppHost-owned dock**. The PostgreSQL workflow above and the Node terminal experiment are intentionally separate. A terminal-looking interface is not enough to make them interchangeable.

An exit code of zero means the tape completed. It does not prove that every program it typed into a shell succeeded. A real smoke test should also verify an application result: an API response, a recorded state transition, or another independent assertion.

After this separate experiment, stop its AppHost explicitly:

```bash
aspire stop --apphost ./apphost.cs --non-interactive
```

Do not use broad process-name cleanup on a machine where other applications may be running.

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
