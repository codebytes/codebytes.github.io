# Parameters Are Inputs, Environment Variables Are Delivery

> Editorial status: draft for external publication, not for this site's content feed. Examples target Aspire 13.6.1 and a C# AppHost.

A developer adds an environment variable to an API. The application starts, reads the setting, and behaves correctly. Later, someone asks where that value comes from in a deployment.

The answer is less obvious than the code makes it look.

Is this a fixed setting? Something the person deploying the application must supply? A secret? An address produced by another resource? A value copied from the developer's machine when the deployment artifacts were generated?

In Aspire, parameters and environment variables can participate in the same configuration path. That does not make them interchangeable. One describes an input to the application model. The other describes how a particular process receives a value.

Confusing those responsibilities is how a clean local configuration becomes an undocumented deployment dependency.

## Start with the question, not the API name

Consider a catalog API that serves a particular business region. The application expects a configuration key named `Catalog:Region`.

There are two separate decisions:

- Who supplies the region for this instance of the application?
- How does the API receive the selected value?

An Aspire parameter can answer the first question. An environment variable can answer the second.[^parameters]

The AppHost connects them:

```csharp
var region = builder.AddParameter("catalogRegion")
    .WithDescription("The business region served by this catalog.");

var api = builder.AddProject<Projects.Api>("api")
    .WithEnvironment("Catalog__Region", region);
```

This is an AppHost fragment. `Projects.Api` represents an existing project referenced by the AppHost; the declarations belong before `builder.Build().Run()`.

`catalogRegion` is the model's input name. `Catalog__Region` is the API process's environment-variable name. Neither has to be the same as the other.

Passing the parameter builder to `WithEnvironment` preserves a reference to that input. The AppHost is not just copying a string at this line of code.

That distinction matters when the value is resolved later, or when a publisher needs to represent it as a deployment input rather than embed today's local value.

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

The same operating-system mechanism appears twice in that table. The scopes are different.

Setting `Parameters__catalogRegion` for the AppHost does not declare a workload setting named `Catalog__Region`. Some local processes can inherit environment values, but that is not a portable deployment contract. The `WithEnvironment` declaration is the bridge.

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

This fragment belongs in the API's startup code, where `builder` is its `WebApplicationBuilder`. A parameter can make a value discoverable and describable. It does not prove that the value makes sense to the application.

A region that is non-empty but unsupported still needs domain validation. A timeout still needs a valid range. An external URL still needs an appropriate scheme and destination policy.

## `WithEnvironment` does not imply "hard-coded"

Environment variables are not the weaker alternative to parameters. They are often the correct delivery mechanism.

`WithEnvironment` can receive a literal, a parameter reference, an endpoint reference, or another supported expression. What you pass determines whether the value is fixed or derived.

A deliberately fixed application setting can be straightforward:

```csharp
api.WithEnvironment("Logging__LogLevel__Default", "Warning");
```

There is no requirement to turn every setting into a deployment parameter. Doing that can create a large configuration surface without a clear owner.

A parameter is useful when a value should be an explicit input to the model. A literal is useful when the AppHost intentionally fixes the value. A resource reference is useful when the model should derive the value from another resource.

The question is not "Which API is more powerful?" It is "Which contract do I mean?"

For a dependency's address or connection information, start with `WithReference` or an endpoint reference rather than asking an operator to maintain a second copy of it. Relationships already in the model should not become unrelated configuration chores.

## Do not collapse a reference into a local value too early

Suppose the AppHost reads its current configuration into a string and then passes that string to the API. That can work perfectly in a local run.

It can also change the deployment contract.

The publisher now sees the supplied literal rather than the parameter reference that would have described a deployment input. A development value can become part of generated configuration instead of something the deployment resolves.

Reading configuration directly is not forbidden. It is appropriate when the AppHost itself needs a setting to choose how to compose the model. But that is different from preserving an externally supplied value for a workload.

Keep the layers visible:

- **Composition settings** tell the AppHost which resources or options to declare.
- **Model parameters** describe values supplied to those declarations.
- **Workload environment variables** deliver values to individual processes.

An application can legitimately use all three. The mistake is assuming that reading a value from configuration automatically gives it parameter semantics.

## The value overload is not a configuration fallback

There is an especially easy trap in a small sample:

```csharp
var localRegion = builder.AddParameter("catalogRegion", "local");
```

In the 13.6.1 implementation, this string-value overload supplies a runtime value through a value getter. It is not the configuration-backed overload with a fallback value.[^implementation]

Do not assume that adding `Parameters__catalogRegion` will override that supplied runtime value. If you want ordinary configuration to select the value, use the configuration-backed declaration shown earlier and put a non-secret development value in the AppHost's configuration.

The overload also has a `publishValueAsDefault` option. That controls whether its supplied value is published as a default; it should not be confused with runtime configuration precedence. Secret parameters and published default values are mutually exclusive.

This is worth noticing before a sample grows into an application. Two declarations can look like they differ only in convenience while making different promises about where the value comes from.

## Naming can make precedence surprising

The examples use `catalogRegion` so the parameter name works without normalization. Parameter names follow Aspire's resource-name constraints; an underscore that is valid in an environment-variable name is not valid in a logical resource name.

Aspire 13.6.1 also supports dash-to-underscore normalization when resolving configuration-backed parameters. A parameter named `catalog-region` can use the normalized `Parameters__catalog_region` spelling when the original configuration key has no value.

That is a fallback between two keys, not a provider-by-provider comparison of both spellings. The implementation checks the exact key first, then its normalized form.[^normalization]

If JSON supplies `Parameters:catalog-region` and the environment supplies only `Parameters:catalog_region`, the exact-key lookup can still find the JSON value. The higher-priority provider contains a different key.

Avoid configuring both spellings and expecting them to behave like one interchangeable override. Consistent portable names are easier to reason about.

Within a single key, the AppHost's configured providers determine precedence. Under the usual defaults, environment values can override JSON values, but custom providers and command-line configuration still matter. A parameter does not create a separate configuration hierarchy.

## Secret parameters are metadata, not a vault

A secret input can be modeled explicitly:

```csharp
var partnerKey = builder.AddParameter("partnerApiKey", secret: true);

api.WithEnvironment("Partner__ApiKey", partnerKey);
```

`secret: true` tells Aspire and the selected deployment integration that this value needs secret treatment. It affects behavior such as masking and how a supported publisher represents the input.

It does not select a secret store, encrypt every copy, or make the API's environment inaccessible.

If a secret is delivered as an environment variable, the workload still receives the value. Debuggers, process inspection, diagnostic exports, and application logging can expose it. A secret-looking field in a dashboard is not an end-to-end data-protection policy.

Keep the source and delivery decisions separate. A local secret store, a CI secret, and a managed production secret service have different lifecycles. Supplying a new value is also not automatically rotating a credential in the service that accepts it.

When the workload and backing service support identity-based access, that may be a better contract than distributing another shared secret.

## Publishing preserves intent, not necessarily today's value

The useful result of the parameter-backed declaration is not that every target generates the same environment-variable file.

It is that the publisher knows a workload setting depends on an input.

An Azure target can represent that input in its provisioning model. A Compose publish can leave a placeholder for later resolution. A target may use a secret-specific representation for a secret parameter.

The details belong to the selected integration. Do not assume that every publish prompts for every value, creates a vault, or produces ready-to-run artifacts with all secrets resolved.

Inspect the generated output for the distinction you intended:

- Is the region still an input, or has a local value been embedded?
- Does the API receive `Catalog__Region`, rather than an unrelated AppHost key?
- Is a secret represented appropriately for the target?
- Does the deployment have an explicit source for required values?

Those questions are more useful than asking whether the environment-variable name appeared somewhere in the output.

## A smaller, clearer configuration surface

When reviewing an AppHost, I want to be able to explain each setting in one sentence.

This is an input supplied by the person or system deploying the application. This is a fixed application setting. This is an address derived from a dependency. This is a composition decision the AppHost makes before any workload starts.

If the explanation depends on an undocumented value inherited from one developer's shell, the model still has work to do.

Parameters and environment variables are not competing configuration systems. Parameters describe the input contract. Environment variables are one way to deliver the resulting value.

The process may receive a string either way. The difference is whether the rest of the application model still knows what that string means.

[^parameters]: [Aspire external parameters](https://aspire.dev/fundamentals/external-parameters/) describes configuration-backed inputs, secret metadata, and passing parameter references to workloads.

[^configuration]: [ASP.NET Core configuration](https://learn.microsoft.com/aspnet/core/fundamentals/configuration/) explains configuration providers and the double-underscore environment-variable convention. [Aspire environment variables](https://aspire.dev/fundamentals/environment-variables/) covers resource-derived configuration.

[^implementation]: The [13.6.1 parameter builder implementation](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting/ParameterResourceBuilderExtensions.cs) distinguishes configuration-backed parameters, supplied values, generated defaults, and published defaults.

[^normalization]: The [13.6.1 configuration helper](https://github.com/microsoft/aspire/blob/v13.6.1/src/Shared/IConfigurationExtensions.cs) defines the exact-key-first normalization behavior.
