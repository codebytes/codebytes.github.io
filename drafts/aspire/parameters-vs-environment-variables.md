# Parameters vs. appsettings.json vs. Environment Variables in Aspire

> Draft for external publication, outside this site's content feed. The C# AppHost fragments target Aspire 13.6.1. Compose output comes from `aspire publish`; nothing was deployed.

A catalog API needs to know which region it serves. In an Aspire application, `Catalog:Region` could go in four places: the API's `appsettings.json`, the AppHost's `appsettings.json`, an AppHost parameter, or a `WithEnvironment` call.

Three of those work during `aspire run`. One never reaches the API. After `aspire publish`, those three behave differently: one value ships inside the API, one becomes a deployment input, and one is written into the output exactly as you typed it.

## Four places, four behaviors

| Where the value lives      | Who reads it           | After `aspire publish`               |
| -------------------------- | ---------------------- | ------------------------------------ |
| API `appsettings.json`     | The API, at startup    | Ships with the API build             |
| AppHost `appsettings.json` | The AppHost            | Stays behind; services never read it |
| Parameter (`AddParameter`) | The AppHost model      | Becomes a deployment input           |
| `WithEnvironment`          | One resource's process | Written for that resource as passed  |

The two `appsettings.json` files cause most of the confusion, so start there.

## The API's appsettings.json: defaults that ship with the code

The API reads its own `appsettings.json` at startup, and the file is copied into the published app. Use it for defaults that are correct everywhere:

```json
{
  "Catalog": {
    "PageSize": 20
  }
}
```

A region is a poor fit. If a deployment forgets to supply one, a default here lets the API start and serve the wrong region instead of failing.

Environment-specific files need care too. `appsettings.Development.json` loads only when the API's environment is `Development`. The Compose service that Aspire 13.6.1 generated for the API didn't set `ASPNETCORE_ENVIRONMENT`, so the container runs as `Production` and ignores that file. A value that exists only in the Development file disappears after publishing.

## The AppHost's appsettings.json: configuration for the AppHost

The AppHost reads its own configuration. Values in its `appsettings.json` don't reach the API or any other resource unless the AppHost passes them along. The generated Compose service for the API contained only the variables the AppHost set for it.

Two kinds of values belong in this file:

- Local values for parameters, under the `Parameters` section.
- Switches the AppHost reads to decide what to model, such as whether to add a diagnostic tool.

```json
{
  "Parameters": {
    "catalogRegion": "local"
  }
}
```

Keep secrets out of it. `aspire secret set` stores them in the AppHost's user secrets instead.

## Parameters: values each environment must supply

A parameter is an input to the application model:

```csharp
var region = builder.AddParameter("catalogRegion")
    .WithDescription("The business region served by this catalog.");

var api = builder.AddProject<Projects.Api>("api")
    .WithEnvironment("Catalog__Region", region);
```

During a local run, the AppHost resolves `Parameters:catalogRegion` from its configuration sources, including `appsettings.json`, user secrets, and environment variables. Setting `Parameters__catalogRegion` in the AppHost's environment overrides the JSON value, as usual. If no source has a value, the dashboard shows **Unresolved parameters**, asks for the value, and offers to save it to user secrets.[^parameters]

Publishing is where the parameter pays off. With a Docker Compose target, Aspire 13.6.1 wrote the API's variable as a placeholder:

```yaml
Catalog__Region: "${CATALOGREGION}"
```

The generated `.env` file had an empty `CATALOGREGION=` entry. The `local` value from the AppHost's `appsettings.json` didn't come along, and publishing succeeded without any value. Whoever deploys the files supplies the region.

If the AppHost's configuration already uses a different key, back the parameter with it:

```csharp
var region = builder.AddParameterFromConfiguration("catalogRegion", "Catalog:Region");
```

That reads `Catalog:Region` from the AppHost's configuration, not the API's.

Mark credentials as secret:

```csharp
var partnerKey = builder.AddParameter("partnerApiKey", secret: true);

api.WithEnvironment("Partner__ApiKey", partnerKey);
```

```bash
aspire secret set Parameters:partnerApiKey "<value>"
```

The dashboard masks the value, and the Compose output had only `${PARTNERAPIKEY}` with an empty `.env` entry. The API still receives the key as an environment variable, so anything that can inspect that process can read it.

## WithEnvironment: delivering the value

`WithEnvironment` sets a variable on one resource's process. ASP.NET Core maps the double underscore to a section separator, so `Catalog__Region` arrives as `Catalog:Region`. Environment variables load after the JSON files in the default configuration, so this value overrides both `appsettings.json` and `appsettings.{Environment}.json` in the API.[^configuration]

Two processes read environment variables in this example. `Parameters__catalogRegion` configures the AppHost's parameter; `Catalog__Region` is what the API receives.

What you pass decides what gets published. A parameter stays a parameter, and a literal stays a literal:

```csharp
api.WithEnvironment("Logging__LogLevel__Default", "Warning");
```

That produced `Logging__LogLevel__Default: "Warning"` in the Compose output, which is right when the AppHost should fix the value everywhere.

For another resource's address or connection string, use `WithReference`. The AppHost already knows those values, so nobody should have to type them in again.

## Three common surprises

### Copying configuration into a string

```csharp
var region = builder.Configuration["Parameters:catalogRegion"];

api.WithEnvironment("Catalog__Region", region);
```

This behaves the same during `aspire run`. At publish time, Aspire sees only a string, so the Compose output contained `Catalog__Region: "local"`. Your laptop's value became part of the deployment artifacts.

Reading `builder.Configuration` directly is fine when the AppHost needs a setting to decide what to model. Pass the parameter itself when the deployment should supply the value.

### Treating the value overload as a default

```csharp
var region = builder.AddParameter("catalogRegion", "local");
```

This looks like a parameter with a default, but in 13.6.1 the supplied value replaces configuration.[^implementation] With `Parameters__catalogRegion=west` set for the AppHost, the parameter still resolved to `local`. Compose still wrote `${CATALOGREGION}` with an empty `.env` entry, so the value is fixed locally and missing when deployed. Use the configuration-backed overload and put the local value in the AppHost's `appsettings.json`.

### Mixing dashed and underscored names

Aspire falls back from `Parameters:catalog-region` to `Parameters:catalog_region`, which helps where shells don't allow dashes in variable names. The fallback only runs when the original key has no value.[^normalization] With `Parameters:catalog-region` in the AppHost's JSON and `Parameters__catalog_region` in its environment, the JSON value won, even though environment variables normally take precedence. Pick one spelling per parameter, or avoid dashes in parameter names.

## Choosing quickly

- A default that's correct in every environment: the API's `appsettings.json`.
- A value each environment must supply: a parameter, delivered with `WithEnvironment`.
- Another resource's address or connection string: `WithReference`.
- A setting that changes what the AppHost models: the AppHost's configuration, read with `builder.Configuration`.
- A value the AppHost deliberately fixes: a `WithEnvironment` literal.
- A secret: a secret parameter, with the local value stored by `aspire secret set`.

Then publish once and read the output. Each `${...}` placeholder is something a deployment has to provide. Each literal is a value you chose in the AppHost.

[^parameters]: [Aspire external parameters](https://aspire.dev/fundamentals/external-parameters/) covers configuration-backed and secret parameters. The 13.6.1 [parameter processor](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting/Orchestrator/ParameterProcessor.cs) implements the dashboard prompt, and [`aspire secret set`](https://aspire.dev/reference/cli/commands/aspire-secret-set/) writes AppHost user secrets.

[^configuration]: [ASP.NET Core configuration](https://learn.microsoft.com/aspnet/core/fundamentals/configuration/) describes the default provider order and the double-underscore convention.

[^implementation]: The [13.6.1 parameter builder](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting/ParameterResourceBuilderExtensions.cs) implements the configuration-backed, value, and `AddParameterFromConfiguration` overloads.

[^normalization]: The [13.6.1 configuration helper](https://github.com/microsoft/aspire/blob/v13.6.1/src/Shared/IConfigurationExtensions.cs) checks the exact key before the normalized one.
