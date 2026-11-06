---
title: "A Polyglot App Is More Than a Process List"
draft: false
date: "2026-11-06T12:39:26-05:00"
lastmod: "2026-11-06T12:39:26-05:00"
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
description: "Use Aspire 13.6.4 to wire Vite, .NET, and PostgreSQL, then follow a deliberate failure to separate configuration, readiness, and request telemetry."
---

Starting a frontend, an API, and a database is straightforward. Knowing which address each process should use, when its dependencies are ready, and where a failed request went is the harder part.

In the catalog companion, **Load catalog** can return HTTP 503 while the API and inventory service both report healthy. Nothing has to crash for the application to fail.

<!--more-->

In [part one](/posts/aspire-field-notes-keep-the-failing-run/), we kept a failed catalog request. This time, let's look at the wiring that made the request possible and the evidence that tells us which part failed.

Aspire puts the service relationships in the AppHost. The language integrations help, but each service still has to use the configuration it receives and report what happens inside it.

The runnable path in this article was validated with **Aspire 13.6.4**: a Vite frontend, a .NET catalog API, PostgreSQL, and a .NET inventory service. Java and Rust appear later as optional preview examples, not extra requirements for running the companion.

## Three contracts, not one

An AppHost relationship can serve several purposes, but they are not interchangeable:

| Contract      | What it answers                                | What it does not prove                                   |
| ------------- | ---------------------------------------------- | -------------------------------------------------------- |
| Configuration | How does this consumer find its dependency?    | That the dependency is ready or the caller is authorized |
| Readiness     | When is it reasonable to start the consumer?   | That every later request will succeed                    |
| Telemetry     | Can we follow an operation through the system? | That launching a process instrumented all its code       |

`WithReference` supplies configuration, `WaitFor` gates startup, and OpenTelemetry lets us follow the request. A reference can be correct while the dependency is still starting; both can work while the trace is missing.

David Fowler's [developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) makes the broader case: describe the relationships that otherwise live in shell history and a teammate's memory. You can adopt that model incrementally.

## Start with the companion

Use the [sample README](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes) for prerequisites and the one-time PostgreSQL secret setup. Run all commands below from `aspire-field-notes/`.

To run the companion, select the catalog AppHost explicitly because the repository also contains a separate terminal AppHost:

```bash
apphost=catalog/Catalog.AppHost/Catalog.AppHost.csproj
aspire start --apphost "$apphost" --isolated
```

The `apphost` variable keeps the path reusable for later commands; only `aspire start` launches the application. In the dashboard, wait for **web** to become **Healthy**, open its HTTP endpoint, and click **Load catalog**. The [optional CLI checks](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/02-model-the-whole-app#optional-cli-verification) automate readiness and the catalog request; they are not extra startup requirements.

## Follow the catalog's service graph

For one **Load catalog** request, the shape of the app is:

{{< mermaid >}}
flowchart TB
accTitle: Catalog request flow
accDescr: The browser calls the Vite frontend. Vite proxies to the catalog API, which queries catalogdb in PostgreSQL and then calls inventory.

browser["Browser"]
web["web: Vite frontend and proxy"]
api["api: .NET catalog API"]
inventory["inventory: .NET service"]
catalogdb[("catalogdb (PostgreSQL)")]

browser -->|"GET /api/catalog"| web
web -->|"HTTP via API_HTTP"| api
api -->|"SQL query"| catalogdb
api -->|"GET /inventory"| inventory
{{< /mermaid >}}

The arrows show request traffic, not startup order. The API reads `catalogdb`, hosted by the `postgres` resource, before calling inventory. The AppHost supplies configuration and readiness relationships; it is not an HTTP hop in this path.

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

This focused excerpt from the AppHost shows the API's request wiring. `catalogdb` and `inventory` are defined earlier in that file:

```csharp
var api = builder.AddProject<Projects.Catalog_Api>("api")
    .WithReference(catalogdb)
    .WithReference(inventory)
    .WithHttpHealthCheck("/health")
    .WaitFor(catalogdb)
    .WaitFor(inventory);
```

The full AppHost keeps the region and state-volume settings in a separate block for the [configuration/state walkthrough](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/05-portable-state-and-config). The shared API still requires those settings at startup; omitting them from this excerpt is not a request to remove them from the runnable companion.

Selecting **Load catalog** in the frontend makes the browser call `/api/catalog` on its own origin. Vite forwards the request to the API, which reads PostgreSQL and calls inventory once:

{{< figure src="catalog-frontend.png" alt="The companion frontend after Load catalog: 3 products loaded from local, HTTP 200, a trace ID, and a table with the debugging mug, field notebook, and trace sticker" caption="Load catalog returns HTTP 200, three products, and a trace ID to follow in the dashboard." figureClass="full-width" >}}

Open that trace ID in the dashboard to see the database query and the single correlated inventory call. The **Load catalog** command on `web`, whether invoked from the dashboard or the CLI, also goes through the frontend endpoint. It does not bypass Vite to make the API look successful.

### Readiness needs a real check

The companion implements `/health` in the API, inventory service, and Vite server. The API seeds its catalog before accepting traffic, and its database check participates in readiness. Vite uses an actual health middleware, not a catch-all HTML page mistaken for a successful probe.

When adapting the sample, check that each probe's endpoint exists. Otherwise, the dependency will stay unhealthy. At the other extreme, a process with no health checks can satisfy a readiness wait as soon as it is running.

`AddViteApp` handles Vite's development endpoint and port arguments. For other programs, declaring an endpoint and an environment variable only works when the application actually listens on that value.

## Follow configuration into the consumer

The AppHost's `.WithReference(inventory)` gives the API connection information. It does not create an HTTP client. Likewise, `.WithReference(catalogdb)` supplies database configuration but does not register a database client in the API.

The relevant registrations in [`Catalog.Api/Program.cs`](https://github.com/codebytes/blog-samples/blob/main/aspire-field-notes/catalog/Catalog.Api/Program.cs) are:

```csharp
builder.AddServiceDefaults();
builder.AddNpgsqlDataSource("catalogdb");
builder.Services.AddHttpClient("inventory", client =>
{
    client.BaseAddress = new Uri("http://inventory");
    client.Timeout = TimeSpan.FromSeconds(5);
});
```

The API later calls `GetAsync("/inventory")`, so this client needs a base address. `http://inventory` identifies a logical service, not a fixed machine or port. The companion's [Service Defaults](https://github.com/codebytes/blog-samples/blob/main/aspire-field-notes/catalog/ServiceDefaults/Extensions.cs) registers the HTTP service-discovery handler that resolves the actual endpoint from the supplied configuration. `WithReference(inventory)` does not set the client's base address for it. `AddNpgsqlDataSource("catalogdb")` registers the database client using the named connection string.

The API also rejects missing `ConnectionStrings:catalogdb` or `services:inventory:http:0` configuration at startup. It does not quietly substitute a localhost service. Its OpenTelemetry setup lives in Service Defaults and the Npgsql integration; the AppHost reference is not the instrumentation.

For server-side Node, Python, Go, or Rust code, endpoint URL variables are often the simpler contract. A resource named `api` with an endpoint named `http` supplies `API_HTTP`. A named endpoint called `admin` supplies `API_ADMIN`; the suffix is the endpoint's name, not necessarily its scheme.[^environment]

The `services__api__http__0` format serves .NET configuration-based discovery. Do not assume a JavaScript HTTP client understands .NET's logical URI syntax.

Our frontend uses that convention directly. `.WithReference(api)` supplies `API_HTTP`, and the server-side Vite proxy reads it. There is no separate environment-variable alias or hard-coded localhost URL to maintain.

Here is the development wiring for `web`:

```csharp
var web = builder.AddViteApp("web", "../web")
    .WithNpm(installCommand: "ci")
    .WithReference(api)
    .WithHttpHealthCheck("/health")
    .WithExternalHttpEndpoints()
    .WaitFor(api);
```

`WithReference(api)` supplies connection information; `WaitFor(api)` controls startup. Removing one is not a substitute for the other.

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

[`apiTarget`](https://github.com/codebytes/blog-samples/blob/main/aspire-field-notes/catalog/web/proxy-config.mjs) reads `API_HTTP` from the server environment and rejects a missing value or a URL that is not an HTTP(S) origin. It also rejects embedded credentials, a path, query parameters, or a fragment. Browser code calls `/api/catalog` without learning the local API port.

The production build does not need the injected URL. The companion does not use Vite's development or preview server for production; the [deployment walkthrough](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/06-choose-your-deployment) inspects the generated static-site and YARP proxy configuration instead.

Settings with Vite's `VITE_` prefix can be embedded in browser code; they are not an appropriate place for secrets or private server-only configuration.

In the companion run, `API_HTTP` on `web` matched the API's assigned endpoint. The browser's Network panel showed a request to `/api/catalog` on the **web origin**, and no `VITE_*` infrastructure variables were injected. Those checks prove different things: the proxy knows where to send the request, while the browser does not need that internal address.

Inspect just the settings you need in the dashboard. Do not paste the entire resource environment or raw `aspire describe --format Json` output into a report; the API's connection-string fields can contain the PostgreSQL password even when the standalone secret parameter is redacted.

## A green graph can still return 503

The [failure walkthrough](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/01-keep-the-failing-run) restarts the catalog with `Inventory__FaultEnabled=true`. Inventory continues to answer its health probe, but its `/inventory` business endpoint returns a real 503. The catalog API reports **Inventory unavailable** instead of hiding the failure.

Here is what the catalog run showed:

| Scenario                    | API and inventory readiness | Catalog response         | Inventory HTTP attempts |
| --------------------------- | --------------------------- | ------------------------ | ----------------------- |
| Normal request              | Healthy                     | HTTP 200, three products | 1                       |
| Inventory fault enabled     | Healthy                     | HTTP 503                 | 1                       |
| Restart with fault disabled | Healthy                     | HTTP 200, three products | 1                       |

The API queries PostgreSQL before calling inventory, so the database span is present even in the failed request. For each of those three resource-command traces, the evidence was:

- An API server span for `GET /api/catalog`.
- A PostgreSQL query span.
- Exactly one API HTTP client span for the inventory request.
- An inventory server span correlated as that HTTP client's child.

The dashboard's trace view is enough for this walkthrough. If you prefer the CLI, replace `<trace-id>` with the ID returned by **Load catalog**:

```bash
aspire otel spans --apphost "$apphost" --trace-id "<trace-id>" --format Json
```

Vite does not emit application spans in this sample. The browser Network panel verifies the frontend hop; the trace follows the instrumented API, database, and inventory work. Hosting all of them in Aspire does not automatically produce a browser-to-database trace.

The companion deliberately has no HTTP resilience handler, so a catalog request makes one inventory attempt. Disabling the fault and restarting restored HTTP 200 without adding retries. That is a controlled demonstration, not a recommendation to remove retries from every application: choose a retry policy deliberately and check what it actually does.

## What Java and Rust add in 13.6

Aspire 13.6 moves Java and Rust hosting into first-party **preview packages**, building on Community Toolkit contributions. That is different from saying every language feature is generally available.[^release]

The [Java](https://www.nuget.org/packages/Aspire.Hosting.Java/13.6.4-preview.1.26523.11) and [Rust](https://www.nuget.org/packages/Aspire.Hosting.Rust/13.6.4-preview.1.26523.11) hosting packages matching this baseline are **`13.6.4-preview.1.26523.11`**, not stable `13.6.4` packages. With those optional packages referenced, an AppHost can declare:

```csharp
var catalog = builder.AddSpringBootApp("catalog", "../catalog");

var pricing = builder.AddRustApp("pricing", "../pricing")
    .WithHttpEndpoint(env: "PORT");
```

These fragments go before an existing builder's `Build().Run()` and require real applications at those paths. Their package versions and APIs were checked against the published references, but these Java and Rust services were not run as part of the companion. You do not need either toolchain to follow the catalog walkthrough.

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
- An intentional dependency failure stays visible, and any retries match the policy you configured.
- A missing setting fails explicitly rather than falling back to an unrelated localhost service.

A shared dashboard does not apply .NET retry handlers to Go or Node. Browser trace propagation also needs its own setup. Keep those responsibilities visible rather than assuming the graph handles them.

Use [walkthrough 02](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/02-model-the-whole-app) for the detailed configuration and trace checks. When you finish, stop only this AppHost:

```bash
aspire stop --apphost "$apphost"
```

Before adding another language or another box to the graph, make one path explainable when it succeeds and when it fails. That is more useful than a longer list of running processes.

{{% if-published "/posts/aspire-field-notes-terminals-and-repls" %}}
[Next: put diagnostic tools beside those resources](/posts/aspire-field-notes-terminals-and-repls/).
{{% /if-published %}}

[^release]: [Aspire 13.6 announcement and preview boundaries](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/) and [13.4's TypeScript GA and Go hosting milestones](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-4/).

[^environment]: [Aspire environment-variable naming](https://aspire.dev/fundamentals/environment-variables/) and [service discovery](https://aspire.dev/fundamentals/service-discovery/).

[^java]: [Java hosting, framework defaults, instrumentation, and migration](https://aspire.dev/integrations/frameworks/java/java-host/).

[^rust]: [Rust hosting, endpoint configuration, and publishing](https://aspire.dev/integrations/frameworks/rust/rust-host/).
