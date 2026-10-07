---
title: "Aspire 13.6: Service Discovery and Resilience Defaults You Should Change"
date: "2026-10-06"
draft: true
categories:
  - "Development"
tags:
  - "Aspire"
  - "dotnet"
  - "service-discovery"
  - "resilience"
  - "Polly"
  - "HTTP"
  - "distributed-systems"
series:
  - "Aspire Field Notes"
permalink: "/posts/aspire-field-notes-resilience-defaults/"
slug: "aspire-field-notes-resilience-defaults"
aliases:
  - "/2026/09/15/aspire-field-notes-resilience-defaults/"
header:
  teaser: ""
  og_image: ""
excerpt_separator: "<!--more-->"
description: "Tune .NET service discovery and HTTP resilience for Aspire 13.6, make retries safe, budget timeouts, and retain diagnostic runs without stacking handlers."
---

The Aspire Service Defaults project gives a .NET HTTP client a useful starting point: call another service by its logical name and get a resilience pipeline before the first production incident proves you need one.

It is a starting point, not a production policy. Loading a product card and submitting a payment have different latency budgets and retry semantics.

<!--more-->

This is post two of [Aspire Field Notes](/series/aspire-field-notes/), updated for Aspire 13.6.0. The [polyglot tour](/posts/aspire-field-notes-polyglot-tour/) covered resource relationships. Here we will tune the .NET consumer and use the new persisted dashboard runs to inspect the result.

An important boundary: Aspire 13.6 does not move HTTP retry policy into the AppHost or automatically apply .NET resilience to Python, Go, and Node services. The behavior below comes from `Microsoft.Extensions.Http.Resilience` and Polly in the consuming .NET application.

## Start with the generated defaults

The 13.6 Service Defaults template still registers service discovery and one standard resilience handler for factory-created HTTP clients.[^template]

```csharp
public static TBuilder AddServiceDefaults<TBuilder>(this TBuilder builder)
    where TBuilder : IHostApplicationBuilder
{
    builder.ConfigureOpenTelemetry();
    builder.AddDefaultHealthChecks();

    builder.Services.AddServiceDiscovery();

    builder.Services.ConfigureHttpClientDefaults(http =>
    {
        http.AddStandardResilienceHandler();
        http.AddServiceDiscovery();
    });

    return builder;
}
```

This is the method inside the generated Service Defaults project, where the OpenTelemetry and health-check helpers already exist. Each .NET service must reference that project and call `builder.AddServiceDefaults()`. An AppHost reference alone does not register these services.

The standard handler runs the following strategies from outermost to innermost. These are the .NET HTTP resilience library's documented defaults, not new values introduced by Aspire 13.6; check the package version your application restores.[^resilience]

| Strategy                 | Default                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------- |
| Concurrency rate limiter | 1,000 permits, no queue                                                                     |
| Total request timeout    | 30 seconds                                                                                  |
| Retry                    | 3 retries, exponential backoff, 2-second base delay, jitter enabled                         |
| Circuit breaker          | 10 percent failure ratio, 100 minimum throughput, 30-second sampling window, 5-second break |
| Attempt timeout          | 10 seconds                                                                                  |

Three retries means up to four attempts, not three calls in total. The total timeout may end execution before every configured retry happens.

## 1. Start with the caller's deadline

Thirty seconds is a long time on an interactive path. A page waiting for several dependencies can exhaust its user-visible budget before any one downstream service considers itself unhealthy.

Allocate time for the caller's own work, network overhead, and dependencies. A five-second budget might fit one internal operation, while a page that must finish within two seconds clearly needs less. Use measured latency rather than copying a universal number.

The handler's total timeout bounds attempts and retry delays. It is not a substitute for passing the caller's cancellation token. With streaming or `ResponseHeadersRead`, also bound the subsequent response-body consumption; finishing the handler does not guarantee that all application work is complete.

## 2. Make retries safe first

The standard policy handles HTTP 5xx, 408, 429, `HttpRequestException`, and Polly's `TimeoutRejectedException`. It retries every HTTP method by default.[^resilience]

That is dangerous when a request changes state. Retrying after a server accepted an order but lost its response can create another order. Use `DisableForUnsafeHttpMethods()` unless the operation has an explicit idempotency guarantee. It disables retries for `POST`, `PATCH`, `PUT`, `DELETE`, and `CONNECT`; an HTTP method's name is not a substitute for understanding the endpoint.

For deliberately retriable writes, design an idempotency key, deduplication rule, or durable workflow first. Adding retries is the last step, not the first.

## 3. Fit the attempts and delays inside the budget

Here is one illustrative policy for an internal dependency. **Replace** the existing `ConfigureHttpClientDefaults` block inside `AddServiceDefaults` with this block. Do not append a second standard handler elsewhere.

```csharp
builder.Services.ConfigureHttpClientDefaults(http =>
{
    http.AddStandardResilienceHandler(options =>
    {
        options.Retry.DisableForUnsafeHttpMethods();
        options.Retry.MaxRetryAttempts = 2;
        options.Retry.Delay = TimeSpan.FromMilliseconds(100);
        options.Retry.MaxDelay = TimeSpan.FromMilliseconds(200);
        options.TotalRequestTimeout.Timeout = TimeSpan.FromSeconds(5);
        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(1.25);
    });

    http.AddServiceDiscovery();
});
```

For a retriable read, the nominal budget is three attempts at 1.25 seconds plus 100 and 200 milliseconds of backoff: 4.05 seconds before other overhead. Jitter, scheduling, and a server's `Retry-After` response mean this is not a guarantee of exactly three attempts. The total deadline stays in charge.

The short delay and cap are examples, not a recommendation for a throttled public API. Honor the downstream service's rate limits and recovery guidance. A long `Retry-After` may mean returning a useful failure or deferring work instead of waiting inside an interactive request.

Jitter is already enabled by the standard handler. Do not add another jitter implementation or a manual retry loop around it.

## 4. Tune the breaker from traffic

The default circuit breaker needs at least 100 executions during its 30-second sampling window before the failure ratio can open it. That may be too much traffic for a lightly used dependency.

Because the breaker is inside the retry strategy, repeated attempts contribute to its observations. Distinguish downstream attempts from user operations when reading the metrics.

Before changing the thresholds, establish:

- How many attempts reach this dependency during the sampling window?
- Which failures should open the circuit?
- How quickly does the dependency recover?
- What useful response can the caller provide while the circuit is open?

A breaker is not another retry policy. It stops sending work to a dependency that cannot help. Set its sampling window, throughput, ratio, and break duration from the traffic and recovery behavior you observe.

## Keep logical service names

I would keep the discovery model instead of scattering local ports through configuration:

```csharp
builder.Services.AddHttpClient("catalog",
    static client => client.BaseAddress = new Uri("https+http://catalog"));
```

The consuming resource needs `WithReference(catalog)` in the AppHost, and the consumer needs the service-discovery registration shown earlier. Those two pieces connect the logical name to injected endpoint configuration.

For a named HTTPS endpoint called `admin`, use `https://_admin.catalog`. Endpoint names, URI schemes, and resource names have different jobs. Configuration discovery also does not grant permission to call the endpoint.[^discovery]

### Watch the 13.6 connection-string migration

Database and cache connection strings have a separate 13.6 migration concern. A logical name such as `my-db` can have the portable environment-variable alias `ConnectionStrings__my_db`. Stricter deployment targets emit only that portable alias.

Update Aspire client integrations together with the AppHost packages; updated integrations understand the logical-name lookup and portable fallback. A direct `GetConnectionString("my-db")` call or a custom environment-variable reader does not acquire that translation automatically. Keep the reference and consumer on the same explicit portable name, or implement the documented fallback. Names that collapse to the same alias are rejected rather than silently overwriting each other.[^environment]

This is a configuration issue, not a transient network failure. Retries will not repair a missing connection string.

## Replace a policy without stacking another one

Sometimes one client needs a different budget. After calling `AddServiceDefaults()`, remove its inherited resilience handlers and install one deliberate replacement:

```csharp
builder.Services.AddHttpClient("payments",
        static client => client.BaseAddress = new Uri("https+http://payments"))
    .RemoveAllResilienceHandlers()
    .AddStandardResilienceHandler(options =>
    {
        options.Retry.DisableForUnsafeHttpMethods();
        options.TotalRequestTimeout.Timeout = TimeSpan.FromSeconds(3);
        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(1);
    });
```

This removes resilience handlers, not the service-discovery handler already registered by Service Defaults. There is no need to add service discovery a second time.

The example disables automatic retries for unsafe methods; it does not make payments safe on its own. The API still needs authorization, idempotency where appropriate, and a defined recovery path.

Two retry layers can multiply downstream attempts. Two independently configured timeout layers can make failures difficult to interpret. Give ownership of a dependency's retry behavior to one layer and make that ownership visible.

## Keep the evidence with Aspire 13.6

The useful new 13.6 capability here is persisted diagnostic runs, not a new Polly policy. An AppHost dashboard starts in `Run` persistence mode, stores telemetry in SQLite, and lets you reopen earlier runs after restarting the application.[^persistence]

That changes how I would investigate a timeout:

- Reproduce the slow or failing dependency with controlled input and record the operation's correlation information.
- Pin the failing run before changing the policy.
- Change one setting, restart, and repeat the same operation.
- Compare traces, logs, attempt counts, and elapsed time between runs.

Historical runs are read-only, not replayable applications. Ten unpinned runs are retained by default; pinned runs are separate, and telemetry entry limits still apply. A standalone dashboard defaults to temporary `None` mode unless you explicitly choose persistence.

Test the policy itself, not just the happy-path screenshot:

- Return a transient 503 and count the actual downstream attempts.
- Delay a response and confirm that the caller's deadline is respected.
- Make a write succeed while its response is lost, and prove that the recovery design avoids duplicate work.
- Generate enough failures to exercise the breaker, then verify the caller's response while it is open.
- Check malformed configuration and TLS failures separately instead of treating everything as retryable.

The generated .NET Service Defaults already wires common OpenTelemetry instrumentation, with export enabled when the OTLP endpoint is configured. Other languages need their own instrumentation and resilience decisions.

Persisted telemetry can include sensitive values. The dashboard's on-disk database has no independent encryption or authorization layer; protect the directory and redact before sharing. Use Application Insights or another suitable backend for production retention and access control, not the local dashboard as a replacement.[^persistence]

## What is next

The next post follows these requests through the observability stack: cross-language trace propagation, comparing retained local runs, and carrying the diagnostic story into Application Insights.

The aim is not to make every request eventually succeed. It is to fail quickly, safely, and predictably when the dependency cannot help.

[^template]: [Service Defaults source at the Aspire 13.6.0 tag](https://github.com/microsoft/aspire/blob/v13.6.0/src/Aspire.ProjectTemplates/templates/aspire-servicedefaults/Extensions.cs).

[^resilience]: [Microsoft's HTTP resilience guidance, defaults, and handler replacement](https://learn.microsoft.com/dotnet/core/resilience/http-resilience).

[^discovery]: [Aspire service discovery and named endpoints](https://aspire.dev/fundamentals/service-discovery/).

[^environment]: [Aspire 13.6 migration notes](https://aspire.dev/whats-new/aspire-13-6/) and [environment-variable naming](https://aspire.dev/fundamentals/environment-variables/).

[^persistence]: [Dashboard persistence, retention, and data protection](https://aspire.dev/dashboard/data-persistence/).
