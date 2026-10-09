---
title: "A Polyglot App Is More Than a Process List"
date: "2026-10-07T09:01:00-04:00"
lastmod: "2026-10-08T23:04:45-04:00"
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
image: "featured.png"
featureImage: "featured.png"
header:
  teaser: "featured.png"
  og_image: "featured.png"
excerpt_separator: "<!--more-->"
description: "Follow one catalog request through Vite, a .NET API, PostgreSQL, and inventory. See where Aspire supplies configuration, waits for readiness, and relies on your instrumentation."
---

Starting four processes is straightforward. Knowing which address each process should use, when its dependencies are ready, and where a failed request went is the harder part.

Aspire puts those relationships in the AppHost. The language integrations help, but each service still has to use the configuration it receives and report what happens inside it.

<!--more-->

In [part one](/posts/aspire-field-notes-keep-the-failing-run/), we kept a failed catalog request. Let's look at the wiring that made that request possible.

## Three contracts, not one

An AppHost relationship can serve several purposes, but they are not interchangeable:

| Contract      | What it answers                                | What it does not prove                                   |
| ------------- | ---------------------------------------------- | -------------------------------------------------------- |
| Configuration | How does this consumer find its dependency?    | That the dependency is ready or the caller is authorized |
| Readiness     | When is it reasonable to start the consumer?   | That every later request will succeed                    |
| Telemetry     | Can we follow an operation through the system? | That launching a process instrumented all its code       |

`WithReference` supplies configuration, `WaitFor` gates startup, and OpenTelemetry lets us follow the request. A reference can be correct while the dependency is still starting; both can work while the trace is missing.

David Fowler's [developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) makes the broader case: describe the relationships that otherwise live in shell history and a teammate's memory. You can adopt that model incrementally.

## Follow the catalog's service graph

The [catalog AppHost project](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/catalog/Catalog.AppHost) models five application resources, plus the `postgres-password` and `catalog-region` parameters:

| Resource    | Role                    | Contract to inspect                                                         |
| ----------- | ----------------------- | --------------------------------------------------------------------------- |
| `postgres`  | Local PostgreSQL server | Container readiness and credentials                                         |
| `catalogdb` | The catalog database    | Connection information supplied to the API                                  |
| `inventory` | Downstream HTTP service | An instrumented business call, separate from its healthy `/health` endpoint |
| `api`       | Catalog API             | Reads PostgreSQL and makes one inventory request for `/api/catalog`         |
| `web`       | Vite frontend           | Same-origin `/api` requests proxied to the API's assigned endpoint          |

The resource list also shows `web-installer`, a child resource that runs `npm ci` for the frontend; `web` waits for it to finish. The dashboard's **Graph** view draws the same model, with relationships as arrows and resource health shown on the nodes:

{{< figure src="resource-graph.png" alt="Aspire dashboard Graph view: the finished web-installer feeds web, web points to api, api points to inventory and catalogdb, and catalogdb belongs to postgres; the application resources have green health badges" caption="Web calls the API; the API depends on inventory and catalogdb. The finished installer is a separate child resource." figureClass="full-width" >}}

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

Start the app and select **Load catalog** in the frontend. The browser calls `/api/catalog` on its own origin; Vite forwards the request to the API, which reads PostgreSQL and calls inventory once:

{{< figure src="catalog-frontend.png" alt="The companion frontend after Load catalog: 3 products loaded from local, HTTP 200, a trace ID, and a table with the debugging mug, field notebook, and trace sticker" caption="Load catalog returns HTTP 200, three products, and a trace ID to follow in the dashboard." figureClass="full-width" >}}

Open that trace ID in the dashboard to see the database query and the single correlated inventory call. You can make the same request with the **Load catalog** command on `web` in the dashboard, or `aspire resource web load-catalog` from a terminal.

The API still needs to use the supplied database configuration. An AppHost reference does not install a database client or register one in the API's dependency-injection container.

The companion implements `/health` in the API, inventory service, and Vite server. The API seeds its catalog before accepting traffic, and its database check participates in readiness. Vite uses an actual health middleware, not a catch-all HTML page mistaken for a successful probe.

When adapting the sample, check that each probe's endpoint exists. Otherwise, the dependency will stay unhealthy. At the other extreme, a process with no health checks can satisfy a readiness wait as soon as it is running.

`AddViteApp` handles Vite's development endpoint and port arguments. For other programs, declaring an endpoint and an environment variable only works when the application actually listens on that value.

## Follow configuration into the consumer

For .NET HTTP clients, service discovery can resolve an address such as `https+http://api` using configuration supplied by a reference. The consumer must also register service discovery, commonly through Service Defaults.

For server-side Node, Python, Go, or Rust code, endpoint URL variables are often the simpler contract. A resource named `api` with an endpoint named `http` supplies `API_HTTP`. A named endpoint called `admin` supplies `API_ADMIN`; the suffix is the endpoint's name, not necessarily its scheme.[^environment]

The `services__api__http__0` format serves .NET configuration-based discovery. Do not assume a JavaScript HTTP client understands .NET's logical URI syntax.

Our AppHost also sets `API_BASE_URL` because the frontend's server-side proxy expects that name. `WithEnvironment` maps the API endpoint to that setting, so the proxy doesn't need a hard-coded localhost URL.

## Keep server configuration out of the browser bundle

The checked-in [`vite.config.mjs`](https://github.com/codebytes/blog-samples/blob/main/aspire-field-notes/catalog/web/vite.config.mjs) provides the health endpoint and configures the development proxy:

<!-- prettier-ignore -->
```javascript
import { defineConfig } from "vite";
import { apiTarget } from "./proxy-config.mjs";

export default defineConfig(({ command }) => ({
  plugins: [{
    name: "field-notes-health",
    configureServer(server) {
      server.middlewares.use("/health", (_request, response) => {
        response.setHeader("Content-Type", "text/plain");
        response.end("Healthy");
      });
    },
  }],
  // Production uses the generated YARP proxy, not a build-time VITE_* API URL.
  server: command === "serve" ? {
    proxy: {
      "/api": {
        target: apiTarget(process.env),
        changeOrigin: true,
      },
    },
  } : undefined,
}));
```

`apiTarget` rejects a missing value or a URL that is not an HTTP(S) origin. It also rejects embedded credentials, a path, query parameters, or a fragment. Browser code calls `/api/catalog` without learning the local API port.

The production build does not need the injected URL. The companion does not use Vite's development or preview server for production; [part six](/posts/aspire-field-notes-choose-your-deployment/) inspects the generated static-site and YARP proxy configuration instead.

Settings with Vite's `VITE_` prefix can be embedded in browser code; they are not an appropriate place for secrets or private server-only configuration.

## What Java and Rust add in 13.6

Aspire 13.6 moves Java and Rust hosting into first-party **preview packages**, building on Community Toolkit contributions. That is different from saying every language feature is generally available.[^release]

With `Aspire.Hosting.Java` and `Aspire.Hosting.Rust` pinned to the `13.6.1-preview.1.26506.6` packages that accompany the 13.6.1 patch, an AppHost can declare:

```csharp
var catalog = builder.AddSpringBootApp("catalog", "../catalog");

var pricing = builder.AddRustApp("pricing", "../pricing")
    .WithHttpEndpoint(env: "PORT");
```

These fragments go before an existing builder's `Build().Run()` and require real applications at those paths. They aren't part of the catalog companion, so you don't need Java or Rust to run it.

Spring Boot uses the application's Maven or Gradle wrapper and receives its port through `SERVER_PORT`. Add an `/actuator/health` check only if the application includes and exposes the corresponding Actuator support. `WithOtelAgent()` is available when you want Java-agent instrumentation; configuring an exporter by itself does not create spans.[^java]

The Rust resource runs Cargo. The Rust server must read `PORT` and expose an appropriate endpoint. The integration supplies OpenTelemetry settings, but the application still needs the Rust SDK and instrumentation. Cargo features, binary selection, and publishing are separate concerns from HTTP endpoint configuration.[^rust]

If you have an existing Java or Rust service, start with that. Verify its endpoint, readiness, and trace before adding more services to the graph.

## Do not confuse two language choices

There is the language of the **AppHost**, and there are the languages of the **services it runs**.

| Choice                            | Position in the 13.6 story                                                          |
| --------------------------------- | ----------------------------------------------------------------------------------- |
| C# or TypeScript AppHost          | Established authoring options; TypeScript reached GA in 13.4                        |
| JavaScript, Python, or Go service | Existing first-party hosting integrations (Go since 13.4); none is new in 13.6      |
| Java or Rust service              | New first-party preview hosting packages                                            |
| Additional AppHost languages      | Experimental, feature-flagged authoring paths                                       |
| Deno                              | Deno 2 can run a TypeScript AppHost; the new Deno guest-hosting API is experimental |

You can write the AppHost in TypeScript and keep the API in C#, or host Rust from a C# AppHost. Pick an authoring language your team can maintain; service-language support is a separate choice.

## Another example: the Node.js weather map

David Pine's [Bluesky post](https://bsky.app/profile/davidpine.dev/post/3mwmut6556k2a) and [Mastodon post](https://dotnet.social/@davidpine/117352196531501696) point to the [official Node.js weather-map sample](https://aspire.dev/reference/samples/aspire-with-node/).

It combines Express and OpenTelemetry, React 19, Vite, Leaflet, and a TypeScript AppHost. The external weather API is modeled too. More importantly, it shows different run and publish arrangements: a development proxy locally, and frontend build output served with the API in the published application.

Follow one weather request and look at how the external API is configured. Before adapting it for production, you'll also need authentication, rate limits, caching, and a plan for the weather provider's quota.

## Prove one path before adding more resources

Take one operation through your application and check:

- The consumer receives an endpoint derived from its resource reference.
- A configured readiness check gates startup where it matters.
- The request reaches the intended dependency.
- Telemetry connects the instrumented hops.
- A missing setting fails explicitly rather than falling back to an unrelated localhost service.

A shared dashboard does not apply .NET retry handlers to Go or Node. Browser trace propagation also needs its own setup. Keep those responsibilities visible rather than assuming the graph handles them.

Use [walkthrough 02](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/02-model-the-whole-app) to follow that path through the catalog app. The setup and exact commands live with the sample.

[Next: put diagnostic tools beside those resources](/posts/aspire-field-notes-terminals-and-repls/).

[^release]: [Aspire 13.6 announcement and preview boundaries](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/) and [13.4's TypeScript GA and Go hosting milestones](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-4/).

[^environment]: [Aspire environment-variable naming](https://aspire.dev/fundamentals/environment-variables/) and [service discovery](https://aspire.dev/fundamentals/service-discovery/).

[^java]: [Java hosting, framework defaults, instrumentation, and migration](https://aspire.dev/integrations/frameworks/java/java-host/).

[^rust]: [Rust hosting, endpoint configuration, and publishing](https://aspire.dev/integrations/frameworks/rust/rust-host/).
