# Customize the Infrastructure, Not the Application Contract

> Editorial status: draft for external publication, not for this site's content feed. Examples target Aspire 13.6.1 and a C# AppHost.

An API uploads a file to local blob storage. The emulator is healthy, the request works, and the developer has a useful feedback loop.

Then the infrastructure review starts.

Which storage redundancy did we choose? Can a blob container allow anonymous access? Which identity can write files? Will the published application still point at a development endpoint?

A passing local request does not answer those questions. An AppHost can describe both the developer experience and the infrastructure the application needs, but those descriptions have different jobs.

The useful goal is not to make a laptop look exactly like Azure. It is to keep the application's dependency contract stable while making the physical implementation and its policies explicit.

## There is more than one kind of configuration

Imagine trying to change an Azure storage account by adding this setting to the API:

```csharp
api.WithEnvironment("Storage__Sku", "Standard_LRS");
```

That declaration delivers a value to the API process. It does not change the SKU of the storage account Aspire provisions.

The application might read the setting for its own purposes. Unless it implements provisioning behavior itself, nothing about that environment variable configures an Azure resource.

There are at least three layers to distinguish:

| Layer                        | Example                                                             | What it controls                           |
| ---------------------------- | ------------------------------------------------------------------- | ------------------------------------------ |
| Application configuration    | A value passed with `WithEnvironment`                               | What the workload reads                    |
| Application model            | Resources, references, endpoints, and readiness                     | What the AppHost composes                  |
| Infrastructure customization | Azure Provisioning properties set through `ConfigureInfrastructure` | What the generated Azure resource declares |

The APIs are related because they describe one application. They are not substitutes for one another.

A reference can connect an API to storage. A readiness relationship can gate local startup. An infrastructure callback can change an Azure storage property. None of those, by itself, proves the deployed application's access policy works.

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

The integration supplies the connection information appropriate to that representation. The API still needs the matching client registration and configuration handling; a resource reference does not instrument or configure arbitrary application code automatically.

The explicit guard makes the local choice easy to see. For Azure Storage specifically, the 13.6.1 `RunAsEmulator` implementation already returns without applying the emulator in Publish mode. The guard documents intent; it is not a workaround for that integration.[^storage]

This is a useful boundary. Changing the backing implementation does not require the API to detect whether it is on a laptop and manufacture a different address.

It also is not proof of equivalence. Azurite does not reproduce Azure networking, managed identity, RBAC, scale, or every service behavior.

## Run mode is not a synonym for Development

The execution context answers what kind of AppHost invocation is taking place. An environment name selects configuration. Those are different axes.

`IsRunMode` and `IsPublishMode` reflect the AppHost's operation, not a comparison with a string such as `Development` or `Production`.[^context]

| Invocation                     | Execution context | Main purpose                                                |
| ------------------------------ | ----------------- | ----------------------------------------------------------- |
| `aspire run` or `aspire start` | Run mode          | Orchestrate the application                                 |
| `aspire publish`               | Publish mode      | Execute the publishing pipeline                             |
| `aspire deploy`                | Publish mode      | Execute the deployment pipeline, including its dependencies |

A local run can use real Azure resources. A publishing operation can select a non-production environment. Changing the configuration environment does not turn one operation into the other.

That is why a check against the environment name is a poor substitute for the emulator choice above.

It is also why `IsPublishMode` does not mean "nothing can change outside this process." Both publication and deployment use the publishing model. The selected pipeline operation and its registered steps determine which work is performed.

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

`Single()` is intentional here: this callback expects exactly one storage account. If a future model change breaks that assumption, a visible failure is better than quietly customizing the wrong construct.

The settings describe a policy and a tradeoff. This example selects locally redundant storage; that is not a universal recommendation for production durability. The required redundancy should follow the workload's recovery requirements.

The explicit TLS minimum also documents a policy that Aspire 13.6.1 already applies by default. Repeating a required value can make the expectation clear without claiming it is a newly added protection.

Defaults are useful starting points. They are not a substitute for deciding which defaults your application relies on.

## Anonymous access, networking, and identity are separate decisions

`AllowBlobPublicAccess = false` disables the account's ability to permit anonymous public access to blobs. It does not make the account's endpoint private.

Public-network access, firewall rules, private endpoints, and DNS have their own configuration. Disabling public-network access without providing a working private path can produce an application that is secure against the developer too.

Identity is another separate layer. Aspire's Azure integrations can generate default role assignments based on resource references, including storage data roles. Review those assignments and the identities receiving them rather than assuming every reference expresses the least privilege your application needs.[^roles]

A deployment identity, an image-pull identity, and the workload's data-access identity can have different responsibilities. Permission to deploy an account is not automatically permission to upload a blob from the application.

The local emulator bypasses much of that operational context. A successful upload there validates the local path, not the Azure authorization design.

## Infrastructure callbacks are not "publish-only hooks"

It can be tempting to wrap every infrastructure customization in `if (builder.ExecutionContext.IsPublishMode)`.

That is not the right default.

A Run-mode application that uses real Azure backing services may also need the same provisioning policy. Guarding the callback by Publish mode can make the resources provisioned for that developer loop differ from the ones provisioned by the deployment workflow.

Use the execution context when the difference is deliberate, such as choosing an emulator for local orchestration. Apply common infrastructure policy to the common resource definition.

`ConfigureInfrastructure` configures a provisioning model. Whether that model is used to generate artifacts or provision resources depends on the operation and integration. It is not a general application startup callback, and its registration alone is not a cloud deployment.

That separation lets reviewers ask useful questions: which policy is shared, which implementation changes, and why?

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

Those are separate decisions, even when they live in the same AppHost file.

## Existing resources are not newly managed resources

Not every storage account should be created by the application.

If the platform team owns an existing resource, referencing it can be the correct contract. Aspire provides mode-aware existing-resource APIs, including `RunAsExisting`, `PublishAsExisting`, and `AsExisting`.[^customization]

An existing declaration identifies a resource to use. It should not be treated as an instruction to retrofit every property from a new-resource customization example onto the deployed account.

Ownership matters here. An application that consumes a shared account may not have authority to change its redundancy, network policy, naming, or lifecycle.

Make that boundary explicit in the model and in the review. "The application needs this service" and "the application manages this service" are different statements.

## Review artifacts without moving the source of truth

A generated Bicep file is valuable evidence. It is not usually the right place to make the durable fix.

If a reviewer wants a different SKU, change the AppHost's customization and regenerate the output. Hand-editing the generated file can leave the code claiming one policy while the next publication restores another.

Publishing deserves its own review. `aspire publish --list-steps` lists the planned steps without executing those steps, but still prepares and evaluates the AppHost. A real publication executes the registered pipeline, which can include builds and custom tooling.[^pipeline]

Inspect the infrastructure output for the actual properties, not merely the presence of a callback in source:

- The intended storage SKU and resource kind are declared.
- Anonymous blob access and the TLS minimum match the policy.
- Endpoint outputs and parameter references are retained.
- Identities and role assignments match their intended responsibilities.
- The cloud model does not accidentally publish the emulator's development endpoints.

A generated template can establish those declarations. It cannot establish that Azure accepted the deployment, that DNS resolves from the workload, or that a particular caller has access.

After an authorized deployment, test an upload with the intended identity, a rejected request from an unauthorized caller, and the data-retention behavior the workload requires.

The article's model and artifact examples do not claim that an Azure deployment has been performed.

## Preserve the contract, make the difference explicit

The API's need for blob storage remains recognizable through the whole workflow.

Run mode can provide an emulator and a fast developer loop. The publishing model can describe Azure Storage with a reviewed policy. Deployment can apply that model using a specific identity and target.

Those stages answer different questions. Treating a successful local run as proof of infrastructure correctness skips the questions that matter later.

The AppHost is most useful when the dependency contract stays stable and the differences are visible in version-controlled code. Customize the infrastructure deliberately, review the generated result, and verify the deployed behavior separately.

[^storage]: The [13.6.1 Azure Storage implementation](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting.Azure.Storage/AzureStorageExtensions.cs) defines the Azurite Run-mode behavior, Azure storage defaults, and generated storage resources.

[^context]: The [13.6.1 execution context](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting/DistributedApplicationExecutionContext.cs) defines Run and Publish operations. [Azure deployment](https://aspire.dev/deployment/azure/) explains the publishing model's target selection and deployment workflow.

[^customization]: [Customize Azure resources](https://aspire.dev/integrations/cloud/azure/customize-resources/) covers typed infrastructure customization, existing resources, and output references.

[^roles]: [Manage Azure role assignments](https://aspire.dev/integrations/cloud/azure/role-assignments/) explains default assignments and explicit customization.

[^pipeline]: [`aspire publish`](https://aspire.dev/reference/cli/commands/aspire-publish/) and [`aspire deploy`](https://aspire.dev/reference/cli/commands/aspire-deploy/) describe the pipeline operations and command options.
