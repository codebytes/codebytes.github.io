---
title: "A Polyglot App Is More Than a Process List"
date: "2026-10-06"
draft: true
categories:
  - "Development"
tags:
  - "Aspire"
  - "JavaScript"
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

The [modeling companion exercise](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/exercises/02-model-the-whole-app) uses the shared catalog app in `blog-samples`. Start with the collection's prerequisites and review checkout, then run the exercise from that checkout's `aspire-field-notes/` directory.

## Three contracts, not one

An AppHost relationship can serve several purposes, but they are not interchangeable:

| Contract      | What it answers                                | What it does not prove                                   |
| ------------- | ---------------------------------------------- | -------------------------------------------------------- |
| Configuration | How does this consumer find its dependency?    | That the dependency is ready or the caller is authorized |
| Readiness     | When is it reasonable to start the consumer?   | That every later request will succeed                    |
| Telemetry     | Can we follow an operation through the system? | That launching a process instrumented all its code       |

`WithReference`, `WaitFor`, and OpenTelemetry each contribute something different. Treating one as a substitute for the others is how a working launcher becomes a confusing application.

David Fowler's [developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) makes the broader case: describe the relationships that otherwise live in shell history and a teammate's memory. You can adopt that model incrementally.

## Start with the companion's service graph

The [catalog AppHost project](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/catalog/Catalog.AppHost) models five named resources:

| Resource    | Role                    | Contract to inspect                                                         |
| ----------- | ----------------------- | --------------------------------------------------------------------------- |
| `postgres`  | Local PostgreSQL server | Container readiness and credentials                                         |
| `catalogdb` | The catalog database    | Connection information supplied to the API                                  |
| `inventory` | Downstream HTTP service | An instrumented business call, separate from its healthy `/health` endpoint |
| `api`       | Catalog API             | Reads PostgreSQL and makes one inventory request for `/api/catalog`         |
| `web`       | Vite frontend           | Same-origin `/api` requests proxied to the API's assigned endpoint          |

Use the checked-in project and service implementations rather than assembling disconnected snippets. The explicit AppHost path from the collection root is `catalog/Catalog.AppHost/Catalog.AppHost.csproj`.

This excerpt from the AppHost shows the API's configuration and readiness wiring. `catalogdb`, `inventory`, and `region` are defined earlier in that file:

```csharp
var api = builder.AddProject<Projects.Catalog_Api>("api")
    .WithReference(catalogdb)
    .WithReference(inventory)
    .WithEnvironment("Catalog__Region", region)
    .WithVolume("catalog-state", "/data", env: "DATA_PATH")
    .WithHttpHealthCheck("/health")
    .WaitFor(catalogdb)
    .WaitFor(inventory);
```

From the collection root, run the full request-path check:

```bash
bash scripts/aspire.sh start \
  --apphost catalog/Catalog.AppHost/Catalog.AppHost.csproj --isolated --non-interactive &&
node scripts/smoke.mjs healthy
```

The check waits for readiness and then verifies the browser-facing route, response shape, database span, and correlated inventory call. A green process alone cannot satisfy it.

The API still needs to use the supplied database configuration. An AppHost reference does not install a database client or register one in the API's dependency-injection container.

The companion implements `/health` in the API, inventory service, and Vite server. The API seeds its catalog before accepting traffic, and its database check participates in readiness. Vite uses an actual health middleware, not a catch-all HTML page mistaken for a successful probe.

When adapting the sample, adding a probe for an endpoint that does not exist makes a dependency look permanently unhealthy. A bare process with no health checks can satisfy a readiness wait once it is running, which is a weaker guarantee than application readiness.

`AddViteApp` handles Vite's development endpoint and port arguments. For other programs, declaring an endpoint and an environment variable only works when the application actually listens on that value.

## Follow configuration into the consumer

For .NET HTTP clients, service discovery can resolve an address such as `https+http://api` using configuration supplied by a reference. The consumer must also register service discovery, commonly through Service Defaults.

For server-side Node, Python, Go, or Rust code, endpoint URL variables are often the simpler contract. A resource named `api` with an endpoint named `http` supplies `API_HTTP`. A named endpoint called `admin` supplies `API_ADMIN`; the suffix is the endpoint's name, not necessarily its scheme.[^environment]

The `services__api__http__0` format serves .NET configuration-based discovery. Do not assume a JavaScript HTTP client understands .NET's logical URI syntax.

The extra `API_BASE_URL` setting in our AppHost is intentional. It maps a specific endpoint to a setting expected by the frontend's server-side proxy. That is a good use of `WithEnvironment`, rather than another hard-coded localhost URL.

## Keep server configuration out of the browser bundle

The checked-in [`vite.config.mjs`](https://github.com/codebytes/blog-samples/blob/codebytes-aspire-companion-samples/aspire-field-notes/catalog/web/vite.config.mjs) provides the health endpoint and configures the development proxy:

```javascript
import { defineConfig } from "vite";
import { apiTarget } from "./proxy-config.mjs";

export default defineConfig(({ command }) => ({
  plugins: [
    {
      name: "field-notes-health",
      configureServer(server) {
        server.middlewares.use("/health", (_request, response) => {
          response.setHeader("Content-Type", "text/plain");
          response.end("Healthy");
        });
      },
    },
  ],
  server:
    command === "serve"
      ? {
          proxy: {
            "/api": {
              target: apiTarget(process.env),
              changeOrigin: true,
            },
          },
        }
      : undefined,
}));
```

`apiTarget` rejects a missing value or a URL that is not an HTTP(S) origin. It also rejects embedded credentials, a path, query parameters, or a fragment. Browser code calls `/api/catalog` without learning the local API port.

The production build does not need the injected URL. The companion does not use Vite's development or preview server for production; [part six](/posts/aspire-field-notes-choose-your-deployment/) inspects the generated static-site and YARP proxy configuration instead.

Settings with Vite's `VITE_` prefix can be embedded in browser code; they are not an appropriate place for secrets or private server-only configuration.

## What Java and Rust add in 13.6

Aspire 13.6 moves Java and Rust hosting into first-party **preview packages**, building on Community Toolkit contributions. That is different from saying every language feature is generally available.[^release]

In a separate AppHost experiment with `Aspire.Hosting.Java` and `Aspire.Hosting.Rust` pinned to the documented `13.6.0-preview.1.26479.8` packages, these resource definitions illustrate the new surface:

```csharp
var catalog = builder.AddSpringBootApp("catalog", "../catalog");

var pricing = builder.AddRustApp("pricing", "../pricing")
    .WithHttpEndpoint(env: "PORT");
```

These are optional integration fragments, not services included in the catalog companion. They go before an existing builder's `Build().Run()` and require real applications at those paths. Running the companion does not require Java or Rust.

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
