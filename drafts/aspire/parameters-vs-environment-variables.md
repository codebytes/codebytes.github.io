# Parameters Are Inputs, Environment Variables Are Delivery

> Draft for external publication, outside this site's content feed. The C# AppHost fragments target Aspire 13.6.1; they are not a standalone runnable sample.

The API reads `Catalog__Region`, gets `local`, and starts successfully. That looks fine during development. At deployment time, though, someone has to decide where the region comes from and whether `local` should still be there.

In Aspire, a parameter describes an input to the application model. An environment variable delivers a value to a particular process. You can use both for the same setting.

The distinction matters to the publisher: a reference to an input can remain configurable at deployment, while a copied local string may end up embedded in the output.

## Decide who supplies the value

Consider a catalog API that serves a particular business region. The application expects a configuration key named `Catalog:Region`.

There are two separate decisions:

- Who supplies the region for this instance of the application?
- How does the API receive the selected value?

An Aspire parameter and an environment variable can handle those two jobs together:[^parameters]

```csharp
var region = builder.AddParameter("catalogRegion")
    .WithDescription("The business region served by this catalog.");

var api = builder.AddProject<Projects.Api>("api")
    .WithEnvironment("Catalog__Region", region);
```

This is an AppHost fragment. `Projects.Api` represents an existing project referenced by the AppHost; the declarations belong before `builder.Build().Run()`.

`catalogRegion` is the model's input name; `Catalog__Region` is the API process's environment-variable name. They serve different readers, so the names don't have to match.

Passing the parameter builder to `WithEnvironment` preserves the reference. A publisher can then represent it as a deployment input rather than copying today's local value.

## Follow the value across the process boundary

For a local development value, the AppHost can have this configuration:

```json
{
  "Parameters": {
    "catalogRegion": "local"
  }
}
```

That JSON belongs to the **AppHost's** configuration, not automatically to the API's.

The parameter reads `Parameters:catalogRegion`. The resource wiring delivers its value through `Catalog__Region`. In an ASP.NET Core application using the normal environment-variable configuration provider, the double underscore maps to a configuration separator, so the API reads `Catalog:Region`.[^configuration]

| Location                                     | Name                        | Responsibility                                       |
| -------------------------------------------- | --------------------------- | ---------------------------------------------------- |
| AppHost configuration                        | `Parameters:catalogRegion`  | Supply the model input                               |
| Environment variable supplied to the AppHost | `Parameters__catalogRegion` | Configure that input through an environment provider |
| API process environment                      | `Catalog__Region`           | Deliver the selected value to the API                |
| API configuration                            | `Catalog:Region`            | Expose the application-facing setting                |

Environment variables appear twice in the table because there are two processes. Setting `Parameters__catalogRegion` for the AppHost doesn't declare `Catalog__Region` for the API. Some local processes can inherit values, but publishing shouldn't depend on that inheritance. The `WithEnvironment` declaration makes the delivery explicit.

Likewise, setting `Catalog__Region` on the API does not create a parameter in the AppHost's deployment model.

The API should validate its own contract:

```csharp
var region = builder.Configuration["Catalog:Region"];

if (string.IsNullOrWhiteSpace(region))
{
    throw new InvalidOperationException(
        "Catalog:Region must be configured.");
}
```

This belongs in the API's startup code, where `builder` is its `WebApplicationBuilder`. It checks that a value arrived. The API should also reject a non-empty region it doesn't support.

## When a literal is enough

`WithEnvironment` accepts literals, parameter references, endpoint references, and other supported expressions. The argument determines whether a setting is fixed or derived.

A deliberately fixed application setting can be straightforward:

```csharp
api.WithEnvironment("Logging__LogLevel__Default", "Warning");
```

If the AppHost intentionally fixes the log level, a literal is sufficient. Making every setting a parameter just gives the person deploying the app more values to manage.

For a dependency's address or connection information, use `WithReference` or an endpoint reference. The model already knows that relationship; asking an operator to supply the same address creates a second copy to keep in sync.

## Keep parameter references intact

Suppose the AppHost reads its current configuration into a string and passes that string to the API. The local run can behave exactly as before, but the publisher now sees a literal rather than a parameter reference. The development value can become part of generated configuration.

Reading configuration directly is appropriate when the AppHost needs to choose which resources or options to declare. For a workload value that should remain a deployment input, pass the parameter reference instead.

Keep the layers visible:

- **Composition settings** tell the AppHost which resources or options to declare.
- **Model parameters** describe values supplied to those declarations.
- **Workload environment variables** deliver values to individual processes.

Reading a setting from configuration does not automatically make it a model parameter.

## The value overload is not a configuration fallback

There is an especially easy trap in a small sample:

```csharp
var localRegion = builder.AddParameter("catalogRegion", "local");
```

In the 13.6.1 implementation, this string-value overload supplies a runtime value through a value getter. It is not the configuration-backed overload with a fallback value.[^implementation]

Do not assume that adding `Parameters__catalogRegion` will override that supplied runtime value. If you want ordinary configuration to select the value, use the configuration-backed declaration shown earlier and put a non-secret development value in the AppHost's configuration.

The overload also has a `publishValueAsDefault` option. That controls whether its supplied value is published as a default; it should not be confused with runtime configuration precedence. Secret parameters and published default values are mutually exclusive.

The two overloads look similar in a short sample, so check which one you're using before relying on a configuration override.

## Naming can make precedence surprising

The examples use `catalogRegion` so the parameter name works without normalization. Parameter names follow Aspire's resource-name constraints; an underscore that is valid in an environment-variable name is not valid in a logical resource name.

Aspire 13.6.1 also supports dash-to-underscore normalization when resolving configuration-backed parameters. A parameter named `catalog-region` can use the normalized `Parameters__catalog_region` spelling when the original configuration key has no value.

That is a fallback between two keys, not a provider-by-provider comparison of both spellings. The implementation checks the exact key first, then its normalized form.[^normalization]

If JSON supplies `Parameters:catalog-region` and the environment supplies only `Parameters:catalog_region`, the exact-key lookup can still find the JSON value. The higher-priority provider contains a different key.

Use one spelling consistently rather than configuring both and expecting a single override chain.

Within a single key, the AppHost's configured providers determine precedence. Under the usual defaults, environment values can override JSON values, but custom providers and command-line configuration still matter. A parameter does not create a separate configuration hierarchy.

## What `secret: true` changes

A secret input can be modeled explicitly:

```csharp
var partnerKey = builder.AddParameter("partnerApiKey", secret: true);

api.WithEnvironment("Partner__ApiKey", partnerKey);
```

`secret: true` affects masking and how a supported publisher represents the input. You still have to choose the secret's source; this flag doesn't create a vault or encrypt every copy.

The workload receives the secret when it's delivered as an environment variable. Debuggers, process inspection, diagnostic exports, and application logging can expose it even when the dashboard masks the value.

Keep the source and delivery decisions separate. A local secret store, a CI secret, and a managed production secret service have different lifecycles. Supplying a new value is also not automatically rotating a credential in the service that accepts it.

When the workload and backing service support identity-based access, that may be a better contract than distributing another shared secret.

## Check what the publisher kept

With the parameter-backed declaration, the publisher knows that a workload setting depends on an input. Each target represents that dependency differently.

An Azure target can represent that input in its provisioning model. A Compose publish can leave a placeholder for later resolution. A target may use a secret-specific representation for a secret parameter.

The details belong to the selected integration. Do not assume that every publish prompts for every value, creates a vault, or produces ready-to-run artifacts with all secrets resolved.

Inspect the generated output for the distinction you intended:

- Is the region still an input, or has a local value been embedded?
- Does the API receive `Catalog__Region`, rather than an unrelated AppHost key?
- Is a secret represented appropriately for the target?
- Does the deployment have an explicit source for required values?

## Follow one setting all the way through

For `Catalog:Region`, the review should be straightforward: who supplies `catalogRegion`, how the publisher represents it, and where the API validates it. `AddParameter` and `WithEnvironment` cover different steps in that path. Keeping the reference between them lets a deployment choose its own region without editing the API or accidentally inheriting `local` from a developer's shell.

[^parameters]: [Aspire external parameters](https://aspire.dev/fundamentals/external-parameters/) describes configuration-backed inputs, secret metadata, and passing parameter references to workloads.

[^configuration]: [ASP.NET Core configuration](https://learn.microsoft.com/aspnet/core/fundamentals/configuration/) explains configuration providers and the double-underscore environment-variable convention. [Aspire environment variables](https://aspire.dev/fundamentals/environment-variables/) covers resource-derived configuration.

[^implementation]: The [13.6.1 parameter builder implementation](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting/ParameterResourceBuilderExtensions.cs) distinguishes configuration-backed parameters, supplied values, generated defaults, and published defaults.

[^normalization]: The [13.6.1 configuration helper](https://github.com/microsoft/aspire/blob/v13.6.1/src/Shared/IConfigurationExtensions.cs) defines the exact-key-first normalization behavior.
