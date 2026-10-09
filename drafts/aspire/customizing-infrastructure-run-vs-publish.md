# Customize the Infrastructure, Not the Application Contract

> Draft for external publication, outside this site's content feed. The C# AppHost fragments target Aspire 13.6.1; they illustrate the model rather than a complete uploads application or an Azure deployment.

An upload works against local blob storage. Before deploying it to Azure, you still need to choose storage redundancy, decide who can upload files, and check whether anonymous access is allowed.

A local emulator can't answer those questions. The AppHost can describe the Azure resource as well as the local dependency, but application settings and infrastructure properties go through different APIs.

We'll keep the API's blob-storage dependency in place while changing how storage is provided for Run and Publish.

## There is more than one kind of configuration

Adding this setting to the API won't change an Azure storage account:

```csharp
api.WithEnvironment("Storage__Sku", "Standard_LRS");
```

That declaration delivers a value to the API process. It does not change the SKU of the storage account Aspire provisions.

The API could read the value, but unless it performs provisioning itself, the storage account remains unchanged.

There are at least three layers to distinguish:

| Layer                        | Example                                                             | What it controls                           |
| ---------------------------- | ------------------------------------------------------------------- | ------------------------------------------ |
| Application configuration    | A value passed with `WithEnvironment`                               | What the workload reads                    |
| Application model            | Resources, references, endpoints, and readiness                     | What the AppHost composes                  |
| Infrastructure customization | Azure Provisioning properties set through `ConfigureInfrastructure` | What the generated Azure resource declares |

A reference supplies storage connection information, a readiness relationship gates startup, and an infrastructure callback changes Azure resource properties. We'll use each where it belongs.

## Keep the dependency visible in both modes

A small uploads application can declare the same storage dependency for local orchestration and Azure publication:

```csharp
var storage = builder.AddAzureStorage("storage");

if (builder.ExecutionContext.IsRunMode)
{
    storage.RunAsEmulator();
}

var uploads = storage.AddBlobs("uploads");

var api = builder.AddProject<Projects.Api>("api")
    .WithReference(uploads)
    .WaitFor(uploads);
```

This is an AppHost fragment. It requires `Aspire.Hosting.Azure.Storage`, an existing referenced API project, and a builder created earlier. The declarations belong before `builder.Build().Run()`.

The API depends on `uploads` in both modes. In this local run, storage uses Azurite. In the Azure publishing model, the resource represents Azure Storage.

The integration supplies the appropriate connection information. The API needs the matching client registration and configuration handling to use it.

The explicit guard makes the local choice easy to see. For Azure Storage specifically, the 13.6.1 `RunAsEmulator` implementation already returns without applying the emulator in Publish mode. The guard documents intent; it is not a workaround for that integration.[^storage]

The API can keep using `uploads` without detecting whether it's on a laptop. Azure networking, managed identity, RBAC, and scale still need separate checks; Azurite doesn't reproduce them.

## Run mode is not a synonym for Development

`IsRunMode` and `IsPublishMode` describe the AppHost operation. An environment name such as `Development` or `Production` selects configuration; it doesn't select the operation.[^context]

| Invocation                     | Execution context | Main purpose                                                |
| ------------------------------ | ----------------- | ----------------------------------------------------------- |
| `aspire run` or `aspire start` | Run mode          | Orchestrate the application                                 |
| `aspire publish`               | Publish mode      | Execute the publishing pipeline                             |
| `aspire deploy`                | Publish mode      | Execute the deployment pipeline, including its dependencies |

A local run can use real Azure resources. A publishing operation can select a non-production environment. Changing the configuration environment does not turn one operation into the other.

Use the execution context for the emulator choice above. Also note that both `publish` and `deploy` use Publish mode: the pipeline operation and its registered steps determine whether they generate artifacts, build code, or change infrastructure.

## Customize the resource Aspire already generates

For Azure resources backed by `AzureProvisioningResource`, `ConfigureInfrastructure` exposes the generated provisioning constructs before their Bicep is emitted.[^customization]

In a C# AppHost, the types come from the Azure Provisioning SDK:

```csharp
using Azure.Provisioning.Storage;

storage.ConfigureInfrastructure(infrastructure =>
{
    var account = infrastructure.GetProvisionableResources()
        .OfType<StorageAccount>()
        .Single();

    account.Sku = new StorageSku
    {
        Name = StorageSkuName.StandardLrs
    };
    account.AllowBlobPublicAccess = false;
    account.MinimumTlsVersion = StorageMinimumTlsVersion.Tls1_2;
    account.Tags["application"] = "uploads";
});
```

Place this after the `storage` declaration and before the AppHost is built. The `using` belongs at the top of the file.

The callback selects the storage account already created by the integration. It does not query Azure to find a live account, and it does not declare a second account.

`Single()` is intentional: this callback expects exactly one storage account. If that changes, it should fail rather than customize the wrong account.

The example chooses locally redundant storage. Select redundancy from your workload's recovery requirements rather than carrying this sample value into production unchanged.

The explicit TLS minimum also documents a policy that Aspire 13.6.1 already applies by default. Repeating a required value can make the expectation clear without claiming it is a newly added protection.

## Anonymous access, networking, and identity are separate decisions

`AllowBlobPublicAccess = false` disables the account's ability to permit anonymous public access to blobs. It does not make the account's endpoint private.

Public-network access, firewall rules, private endpoints, and DNS have their own configuration. If you disable public-network access, provide a private path the workload can actually reach.

Identity is another separate layer. Aspire's Azure integrations can generate default role assignments based on resource references, including storage data roles. Review those assignments and the identities receiving them rather than assuming every reference expresses the least privilege your application needs.[^roles]

A deployment identity, an image-pull identity, and the workload's data-access identity can have different responsibilities. Permission to deploy an account is not automatically permission to upload a blob from the application.

The local emulator bypasses much of that operational context. A successful upload there validates the local path, not the Azure authorization design.

## Infrastructure callbacks are not "publish-only hooks"

A blanket `if (builder.ExecutionContext.IsPublishMode)` guard can skip policy you need in Run mode. A developer using real Azure backing services may need the same storage restrictions as the deployed application.

Use the execution context when the difference is deliberate, such as choosing an emulator for local orchestration. Apply common infrastructure policy to the common resource definition.

`ConfigureInfrastructure` configures a provisioning model. Whether that model is used to generate artifacts or provision resources depends on the operation and integration. It is not a general application startup callback, and its registration alone is not a cloud deployment.

## Select the publishing target separately

An Azure backing resource is not the deployment destination of the API.

For an application targeting Azure Container Apps, the AppHost can declare that compute environment for its publishing model:

```csharp
if (builder.ExecutionContext.IsPublishMode)
{
    builder.AddAzureContainerAppEnvironment("azure");
}
```

This fragment requires `Aspire.Hosting.Azure.AppContainers` and belongs before the AppHost is built. With a single compatible compute environment, Aspire can infer the destination of the API. Multiple environments need explicit assignments.

The mode check keeps this publishing-target declaration out of the local orchestration model. It does not decide whether the storage account uses public networking or which identity can access it.

## Existing resources are not newly managed resources

Not every storage account should be created by the application.

If the platform team owns an existing resource, referencing it can be the correct contract. Aspire provides mode-aware existing-resource APIs, including `RunAsExisting`, `PublishAsExisting`, and `AsExisting`.[^customization]

An existing declaration identifies a resource to use. It should not be treated as an instruction to retrofit every property from a new-resource customization example onto the deployed account.

An application using a platform team's shared account may have no authority to change its redundancy, network policy, naming, or lifecycle. Make the ownership clear before applying a new-resource customization example to it.

## Review artifacts without moving the source of truth

If a reviewer wants a different SKU, change the AppHost and regenerate the Bicep. Editing only the generated file leaves the AppHost unchanged, so the next publish can restore the old value.

Publishing deserves its own review. `aspire publish --list-steps` lists the planned steps without executing those steps, but still prepares and evaluates the AppHost. A real publication executes the registered pipeline, which can include builds and custom tooling.[^pipeline]

Inspect the infrastructure output for the actual properties, not merely the presence of a callback in source:

- The intended storage SKU and resource kind are declared.
- Anonymous blob access and the TLS minimum match the policy.
- Endpoint outputs and parameter references are retained.
- Identities and role assignments match their intended responsibilities.
- The cloud model does not accidentally publish the emulator's development endpoints.

A generated template can establish those declarations. It cannot establish that Azure accepted the deployment, that DNS resolves from the workload, or that a particular caller has access.

After an authorized deployment, test an upload with the intended identity, a rejected request from an unauthorized caller, and the data-retention behavior the workload requires.

The fragments here describe the model and generated declarations. They don't establish those deployed results.

## Keep the API focused on the upload

The API still depends on `uploads`. The AppHost chooses Azurite for the local run and declares Azure Storage policy for provisioning. That keeps environment-specific decisions out of the upload handler and puts them where a reviewer can compare the model, generated Bicep, and deployed behavior.

[^storage]: The [13.6.1 Azure Storage implementation](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting.Azure.Storage/AzureStorageExtensions.cs) defines the Azurite Run-mode behavior, Azure storage defaults, and generated storage resources.

[^context]: The [13.6.1 execution context](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting/DistributedApplicationExecutionContext.cs) defines Run and Publish operations. [Azure deployment](https://aspire.dev/deployment/azure/) explains the publishing model's target selection and deployment workflow.

[^customization]: [Customize Azure resources](https://aspire.dev/integrations/cloud/azure/customize-resources/) covers typed infrastructure customization, existing resources, and output references.

[^roles]: [Manage Azure role assignments](https://aspire.dev/integrations/cloud/azure/role-assignments/) explains default assignments and explicit customization.

[^pipeline]: [`aspire publish`](https://aspire.dev/reference/cli/commands/aspire-publish/) and [`aspire deploy`](https://aspire.dev/reference/cli/commands/aspire-deploy/) describe the pipeline operations and command options.
