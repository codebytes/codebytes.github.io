---
title: "A Polyglot App Is More Than a Process List"
date: "2026-10-06"
draft: true
categories:
  - "Development"
tags:
  - "Aspire"
  - "TypeScript"
  - "dotnet"
  - "Java"
  - "Rust"
  - "OpenTelemetry"
series:
  - "Aspire Field Notes"
series_order: 2
permalink: "/posts/aspire-field-notes-model-the-whole-app/"
slug: "aspire-field-notes-model-the-whole-app"
header:
  teaser: ""
  og_image: ""
excerpt_separator: "<!--more-->"
description: "Model configuration, readiness, and telemetry as separate contracts, then use Aspire 13.6's language integrations without confusing hosting with AppHost authoring."
---

Starting four processes is straightforward. Knowing which address each process should use, when its dependencies are ready, and where a failed request went is the harder part.

That is the interesting polyglot story in Aspire 13.6. Not how many language logos fit on a slide, but whether an existing mixed-language application becomes easier to operate.

<!--more-->

In [part one](/posts/aspire-field-notes-keep-the-failing-run/), we kept the failing run. Now we need a useful model of the application that produced it.

## Three contracts, not one

An AppHost relationship can serve several purposes, but they are not interchangeable:

| Contract      | What it answers                                | What it does not prove                                   |
| ------------- | ---------------------------------------------- | -------------------------------------------------------- |
| Configuration | How does this consumer find its dependency?    | That the dependency is ready or the caller is authorized |
| Readiness     | When is it reasonable to start the consumer?   | That every later request will succeed                    |
| Telemetry     | Can we follow an operation through the system? | That launching a process instrumented all its code       |

`WithReference`, `WaitFor`, and OpenTelemetry each contribute something different. Treating one as a substitute for the others is how a working launcher becomes a confusing application.

David Fowler's [developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) makes the broader case: describe the relationships that otherwise live in shell history and a teammate's memory. You can adopt that model incrementally.

## Start with the services you already have

For the catalog example, assume:

- A .NET project named `CatalogApi`, referenced by the C# AppHost.
- An HTTP launch profile called `http` and an implemented `/health` endpoint.
- A Vite app in `../web`.
- Aspire 13.6.0 hosting packages for PostgreSQL and JavaScript, their required toolchains, and a container runtime.

The AppHost application code can be:

```csharp
var builder = DistributedApplication.CreateBuilder(args);

var database = builder.AddPostgres("postgres")
    .AddDatabase("catalogdb");

var api = builder.AddProject<Projects.CatalogApi>(
        "api", launchProfileName: "http")
    .WithReference(database)
    .WaitFor(database)
    .WithHttpHealthCheck("/health");

builder.AddViteApp("web", "../web")
    .WithReference(api)
    .WithEnvironment("API_BASE_URL", api.GetEndpoint("http"))
    .WaitFor(api);

builder.Build().Run();
```

The API still needs to use the supplied database configuration. An AppHost reference does not install a database client or register one in the API's dependency-injection container.

Likewise, the API must implement `/health`. Adding a probe for an endpoint that does not exist makes a dependency look permanently unhealthy. A bare process with no health checks can satisfy a readiness wait once it is running, which is a weaker guarantee than application readiness.

`AddViteApp` handles Vite's development endpoint and port arguments. For other programs, declaring an endpoint and an environment variable only works when the application actually listens on that value.

## Follow configuration into the consumer

For .NET HTTP clients, service discovery can resolve an address such as `https+http://api` using configuration supplied by a reference. The consumer must also register service discovery, commonly through Service Defaults.

For server-side Node, Python, Go, or Rust code, endpoint URL variables are often the simpler contract. A resource named `api` with an endpoint named `http` supplies `API_HTTP`. A named endpoint called `admin` supplies `API_ADMIN`; the suffix is the endpoint's name, not necessarily its scheme.[^environment]

The `services__api__http__0` format serves .NET configuration-based discovery. Do not assume a JavaScript HTTP client understands .NET's logical URI syntax.

The extra `API_BASE_URL` setting in our AppHost is intentional. It maps a specific endpoint to a setting expected by the frontend's server-side proxy. That is a good use of `WithEnvironment`, rather than another hard-coded localhost URL.

## Keep server configuration out of the browser bundle

Merge this development proxy into the Vite app's existing configuration, preserving its framework plugins and other settings:

```typescript
import { defineConfig } from "vite";

export default defineConfig(({ command, isPreview }) => {
  if (command !== "serve" || isPreview) {
    return {};
  }

  const apiUrl = process.env.API_BASE_URL;
  if (!apiUrl) {
    throw new Error("API_BASE_URL was not configured.");
  }

  return {
    server: {
      proxy: {
        "/api": {
          target: apiUrl,
          changeOrigin: true,
        },
      },
    },
  };
});
```

Browser code can call `/api/products` without learning the local API port. Build and preview modes do not require the AppHost-injected URL.

This is a development proxy. Production needs its own routing arrangement. Also, settings with Vite's `VITE_` prefix can be embedded in browser code; they are not an appropriate place for secrets or private server-only configuration.

## What Java and Rust add in 13.6

Aspire 13.6 moves Java and Rust hosting into first-party **preview packages**, building on Community Toolkit contributions. That is different from saying every language feature is generally available.[^release]

In a separate AppHost experiment with `Aspire.Hosting.Java` and `Aspire.Hosting.Rust` pinned to the documented `13.6.0-preview.1.26479.8` packages, these resource definitions illustrate the new surface:

```csharp
var catalog = builder.AddSpringBootApp("catalog", "../catalog");

var pricing = builder.AddRustApp("pricing", "../pricing")
    .WithHttpEndpoint(env: "PORT");
```

These are fragments added before the existing builder's `Build().Run()`. They assume real applications at those paths, not generated sample services.

Spring Boot uses the application's Maven or Gradle wrapper and receives its port through `SERVER_PORT`. Add an `/actuator/health` check only if the application includes and exposes the corresponding Actuator support. `WithOtelAgent()` is available when you want Java-agent instrumentation; configuring an exporter by itself does not create spans.[^java]

The Rust resource runs Cargo. The Rust server must read `PORT` and expose an appropriate endpoint. The integration supplies OpenTelemetry settings, but the application still needs the Rust SDK and instrumentation. Cargo features, binary selection, and publishing are separate concerns from HTTP endpoint configuration.[^rust]

The useful experiment is to bring **one existing service** into the model and prove its connections. Adding Java and Rust services to an otherwise simple app solely to demonstrate support makes the example harder without making the developer loop better.

## Do not confuse two language choices

There is the language of the **AppHost**, and there are the languages of the **services it runs**.

| Choice                            | Position in the 13.6 story                                                          |
| --------------------------------- | ----------------------------------------------------------------------------------- |
| C# or TypeScript AppHost          | Established authoring options; TypeScript reached GA in 13.4                        |
| JavaScript, Python, or Go service | Existing first-party hosting integrations, not all new in 13.6                      |
| Java or Rust service              | New first-party preview hosting packages                                            |
| Additional AppHost languages      | Experimental, feature-flagged authoring paths                                       |
| Deno                              | Deno 2 can run a TypeScript AppHost; the new Deno guest-hosting API is experimental |

A TypeScript AppHost does not require rewriting the API in TypeScript. A C# AppHost does not turn a Rust service into .NET. Pick the authoring language your team can maintain, then evaluate preview integrations on their own terms.

## Look at a real frontend, not another console message

David Pine's September 29 [Bluesky post](https://bsky.app/profile/davidpine.dev/post/3mwmut6556k2a) and [Mastodon post](https://dotnet.social/@davidpine/117352196531501696) point to the [official Node.js weather-map sample](https://aspire.dev/reference/samples/aspire-with-node/).

It combines Express and OpenTelemetry, React 19, Vite, Leaflet, and a TypeScript AppHost. The external weather API is modeled too. More importantly, it shows different run and publish arrangements: a development proxy locally, and frontend build output served with the API in the published application.

That is a better learning exercise than counting supported languages. Run it, follow one weather request, and identify which component owns each connection.

It remains a demo. Its public endpoints do not supply a production authentication, rate-limiting, caching, or quota strategy.

## Prove one path before adding more resources

Take one operation through your application and check:

- The consumer receives an endpoint derived from its resource reference.
- A configured readiness check gates startup where it matters.
- The request reaches the intended dependency.
- Telemetry connects the instrumented hops.
- A missing setting fails explicitly rather than falling back to an unrelated localhost service.

A shared dashboard does not apply .NET retry handlers to Go or Node. Browser trace propagation also needs its own setup. Keep those responsibilities visible rather than assuming the graph handles them.

[Next: put diagnostic tools beside those resources](/posts/aspire-field-notes-terminals-and-repls/), without turning convenience into unrestricted access.

[^release]: [Aspire 13.6 announcement and preview boundaries](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/) and [13.4's TypeScript GA and Go hosting milestones](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-4/).

[^environment]: [Aspire environment-variable naming](https://aspire.dev/fundamentals/environment-variables/) and [service discovery](https://aspire.dev/fundamentals/service-discovery/).

[^java]: [Java hosting, framework defaults, instrumentation, and migration](https://aspire.dev/integrations/frameworks/java/java-host/).

[^rust]: [Rust hosting, endpoint configuration, and publishing](https://aspire.dev/integrations/frameworks/rust/rust-host/).
