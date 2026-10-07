---
title: "Aspire 13.6 AppHost Polyglot Tour"
date: "2026-10-06"
draft: true
categories:
  - "Development"
tags:
  - "Aspire"
  - "dotnet"
  - "TypeScript"
  - "Python"
  - "Go"
  - "distributed-systems"
  - "OpenTelemetry"
series:
  - "Aspire Field Notes"
permalink: "/posts/aspire-field-notes-polyglot-tour/"
slug: "aspire-field-notes-polyglot-tour"
aliases:
  - "/2026/09/08/aspire-field-notes-polyglot-tour/"
header:
  teaser: ""
  og_image: ""
excerpt_separator: "<!--more-->"
description: "Model a mixed-language application with Aspire 13.6, understand resource references, and use the new diagnostic workflows without confusing previews with stable features."
---

A TypeScript frontend, a .NET API, a Python scoring service, and a Go gateway should not need four unrelated startup recipes. They need one description of how the application fits together.

Aspire 13.6, released September 29, makes that developer loop more useful: dashboard runs survive restarts, interactive tools can live beside your resources, and more language integrations are available. It does not make every workload .NET, nor does it make every new integration production-ready.[^release]

<!--more-->

This is the first post in [Aspire Field Notes](/series/aspire-field-notes/), a series about using Aspire after the quickstart. The examples target Aspire 13.6.0. The focus is the AppHost: what it gives a polyglot team, where the boundaries are, and which parts of the system remain your responsibility.

## Make the developer loop executable

An AppHost describes application resources and their relationships. It is not your production application, and choosing its language does not choose the languages of your services.

David Fowler makes a useful case for incremental adoption in [Your dev loop is full of tribal knowledge](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/): start with shared visibility, model the application, then make repeated operations discoverable. That is a better goal than replacing every script on day one.

For an interactive local session, run `aspire run`. For a script or coding agent, start the app and wait for a resource explicitly:

```bash
aspire start --non-interactive
aspire wait web --timeout 120
```

Use `aspire start --isolated --non-interactive` when working in a separate worktree or when shared local state would be risky. In 13.6, `aspire wait` reports a resource that fails to start rather than leaving automation waiting for an impossible state.[^release]

## One AppHost, several languages

Here is a small C# AppHost. It assumes an existing `Api` project reference, the `Aspire.Hosting.JavaScript`, `Aspire.Hosting.Python`, and `Aspire.Hosting.Go` 13.6 packages, and the corresponding local toolchains.

```csharp
var builder = DistributedApplication.CreateBuilder(args);

var api = builder.AddProject<Projects.Api>("api");

var scoring = builder.AddPythonApp("scoring", "../scoring", "main.py")
    .WithHttpEndpoint(env: "PORT");

var gateway = builder.AddGoApp("gateway", "../gateway")
    .WithHttpEndpoint(env: "PORT")
    .WithReference(api)
    .WithReference(scoring)
    .WaitFor(api)
    .WaitFor(scoring);

var web = builder.AddViteApp("web", "../web")
    .WithReference(gateway)
    .WaitFor(gateway);

builder.Build().Run();
```

The Python and Go servers must listen on the injected `PORT`; declaring an endpoint does not rewrite their application code. `AddViteApp` handles Vite's endpoint and port arguments. Python package-manager selection follows the project files, with `WithUv()` and `WithPip()` available when you need an explicit choice.[^hosting]

Use `AddGoApp` from the first-party `Aspire.Hosting.Go` package, not the deprecated Community Toolkit package or a hand-written `go run` executable resource. Go hosting joined core Aspire in 13.4; it is not a new 13.6 feature.[^go]

`WithReference` supplies configuration. `WaitFor` separately coordinates startup using the resource's readiness information. Without a configured health check, running does not necessarily mean ready to serve requests. Register an appropriate check, such as `WithHttpHealthCheck("/health")` for a service that implements that endpoint.

## Separate hosting support from AppHost authoring

There are two different questions: can Aspire run a service written in a language, and can you write the AppHost itself in that language?

| Capability                                            | Status relevant to this post                                                               |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| C# and TypeScript AppHosts                            | Established authoring choices; TypeScript reached general availability in 13.4             |
| JavaScript, Python, and Go services                   | First-party hosting integrations usable from C# or TypeScript                              |
| Java and Rust services                                | New first-party **preview packages** in 13.6                                               |
| Additional AppHost languages, including Java and Rust | Experimental, feature-flagged authoring paths                                              |
| `AddDotnetProject` and coordinated .NET builds        | Prerelease `Aspire.Hosting.Dotnet` experience; not a required replacement for `AddProject` |

The Java and Rust hosting packages bring framework-aware startup, debugging, and container-publishing support. Java's optional `WithOtelAgent()` supplies automatic instrumentation; configuring telemetry export alone is not the same as instrumenting an application.[^release]

Deno is another distinction worth keeping clear: Deno 2 can run a TypeScript AppHost in 13.6, while the new `AddDenoApp` hosting API is experimental. Do not treat a stable Aspire release as a promise that every API inside it is stable.

## `WithReference` is not `WithEnvironment`

The [Aspire Bytes episode on these APIs](https://youtu.be/1D4PQiW3eqg) is a useful starting point. The practical distinction is:

- Use `WithReference` to supply another resource's connection or endpoint information.
- Use `WithEnvironment` when the consumer expects a particular setting.
- Use `WaitFor` for startup readiness. Neither configuration API substitutes for it.

For a .NET consumer with service discovery configured, the application can use a logical address:

```csharp
builder.Services.AddHttpClient("catalog",
    static client => client.BaseAddress = new Uri("https+http://api"));
```

`https+http` means prefer HTTPS and fall back to HTTP. The consuming resource still needs a reference to `api`. Configuration injection is not global discovery, authentication, or network authorization.[^discovery]

For Node, Python, or Go code reading environment variables directly, use the endpoint URL variables. A resource called `api` with an endpoint called `https` supplies `API_HTTPS`; a named endpoint called `admin` supplies `API_ADMIN`. The suffix is the endpoint name, not necessarily its transport scheme. The `services__api__https__0` form belongs to .NET's service-discovery configuration.[^environment]

For a server-side Node consumer with an HTTPS endpoint configured:

```typescript
const apiUrl = process.env.API_HTTPS;

if (!apiUrl) {
  throw new Error("The API HTTPS endpoint was not configured.");
}

const response = await fetch(new URL("/weather", apiUrl));
if (!response.ok) {
  throw new Error(`The weather request failed: ${response.status}`);
}
```

### Keep the frontend's proxy configuration on the server

Suppose the Vite dev server expects `GATEWAY_URL`. Add this to the earlier AppHost before `Build().Run()`:

```csharp
web.WithEnvironment("GATEWAY_URL", gateway.GetEndpoint("http"));
```

Then merge this development-only proxy into the existing `vite.config.ts`, keeping any framework plugins and other settings in both build and serve modes:

```typescript
import { defineConfig } from "vite";

export default defineConfig(({ command, isPreview }) => {
  if (command !== "serve" || isPreview) {
    return {};
  }

  const gatewayUrl = process.env.GATEWAY_URL;
  if (!gatewayUrl) {
    throw new Error("GATEWAY_URL was not configured.");
  }

  return {
    server: {
      proxy: {
        "/api": {
          target: gatewayUrl,
          changeOrigin: true,
        },
      },
    },
  };
});
```

Browser code can request `/api/weather` without knowing Aspire's local ports. Build and preview modes do not require Aspire's injected gateway URL. This is a development proxy, not production routing; configure the deployed frontend's routing separately.

Avoid using a `VITE_` variable for secrets: those values can be embedded in the browser bundle. Deriving a server-side setting from `GetEndpoint("http")` avoids both hard-coded addresses and an unnecessary browser-visible configuration path.

## The 13.6 improvements I would actually use

### Keep the failing run

An AppHost-launched dashboard now uses SQLite-backed run persistence by default. Restarting the application creates a new run without discarding the previous diagnostic session. Pin an important reproduction before changing code.

The default retention is ten **unpinned** runs per application; pinned runs do not count toward that limit. Console logs, structured logs, and traces each default to 100,000 entries, so persistence is not unlimited history. Historical runs are read-only.[^persistence]

A standalone dashboard still defaults to temporary storage. To resume one standalone database across restarts:

```bash
aspire dashboard run --application-name field-notes --persistence Resume
```

`Resume` reuses one database; it does not provide the separate-run selector of `Run` mode. Keep the application name, data directory, and mode consistent.

### Bring diagnostic tools to the resource

Resource terminals arrived in 13.5. In 13.6, AppHost-owned docked terminals and opt-in database/cache REPLs make it easier to inspect a local dependency without installing another client. Mitch Denny's [terminal walkthrough](https://devblogs.microsoft.com/aspire/aspire-terminal-support/) shows the distinction.

The terminal APIs remain experimental. A `WithRepl()` session uses the resource's real credentials and can write data. Enable it only for trusted local workflows, and exit the client explicitly; closing its viewer is not the same as stopping the client.

### Use one volume setting locally and in a container

If the API writes files, extend the existing resource:

```csharp
api.WithVolume("api-data", "/data", env: "DATA_PATH");
```

In a local process, `DATA_PATH` points to a workload-specific directory. In the published container, it points to `/data`. The application reads one setting rather than guessing where it is running.[^release]

## A community example worth opening

David Pine highlighted a [Node.js weather-map sample on Bluesky](https://bsky.app/profile/davidpine.dev/post/3mwmut6556k2a) and [Mastodon](https://dotnet.social/@davidpine/117352196531501696) on September 29. The [sample](https://aspire.dev/reference/samples/aspire-with-node/) combines an Express API with OpenTelemetry, React 19, Vite, Leaflet, and a TypeScript AppHost.

What interests me is not another weather endpoint. It models an external API, wires the frontend to the backend, and makes backend telemetry visible in one developer loop. Its run-mode proxy and publish-mode container layout also show why local wiring and production routing are related but not identical.

Treat it as a teaching sample, not a security baseline: it deliberately leaves out production authentication, rate limiting, caching, and an upstream quota strategy.

## The work Aspire does not remove

Starting a process does not automatically instrument every HTTP request inside it. A polyglot application still needs language-appropriate OpenTelemetry instrumentation and trace propagation. A shared dashboard does not give Node or Go the .NET `HttpClient` resilience pipeline.

Start with one end-to-end request:

- Instrument the gateway and scoring service, including outgoing calls.
- Use `AddServiceDefaults()` in the .NET API.
- Verify trace context across the hops you instrument; browser tracing requires its own setup.
- Check graceful shutdown and a useful health signal for each service.

The security boundary remains yours, too. Keep secrets in an appropriate secret store, reference them rather than copying them into source, and treat logs and traces as potentially sensitive. The persisted dashboard database has no separate encryption or authorization layer. Protect its directory and redact diagnostic data before sharing it.[^persistence]

Aspire is still not a universal replacement for Docker Compose or a Kubernetes-specific development loop. Use it when the problem is describing, running, and diagnosing the application you own.

## What is next

The [second post](/posts/aspire-field-notes-resilience-defaults/) follows those references into the .NET HTTP pipeline: safe retries, timeout budgets, circuit breakers, and using 13.6's retained runs to inspect failures.

The series then moves through observability, secrets, deployment choices, and AI-provider reliability. For broader polyglot examples, see [the repository behind my Aspire talk](https://github.com/codebytes/aspire-polyglot); check older samples against the 13.6 APIs used here.

[^release]: [Aspire 13.6 release announcement](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/), [full changes and migration notes](https://aspire.dev/whats-new/aspire-13-6/), and [versioned release](https://github.com/microsoft/aspire/releases/tag/v13.6.0).

[^hosting]: [Python hosting](https://aspire.dev/integrations/frameworks/python/) and [JavaScript hosting](https://aspire.dev/integrations/frameworks/javascript/).

[^go]: [First-party Go hosting and migration guidance](https://aspire.dev/integrations/frameworks/go/go-host/).

[^discovery]: [Aspire service discovery](https://aspire.dev/fundamentals/service-discovery/).

[^environment]: [Environment-variable naming and configuration injection](https://aspire.dev/fundamentals/environment-variables/).

[^persistence]: [Dashboard persistence modes, retention, and data protection](https://aspire.dev/dashboard/data-persistence/).
