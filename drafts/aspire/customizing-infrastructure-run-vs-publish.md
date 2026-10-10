# Customizing Azure Infrastructure From the Aspire AppHost

> Draft for external publication, outside this site's content feed. The C# AppHost fragments target Aspire 13.6.1. Bicep excerpts come from `aspire publish`; nothing was deployed.

An upload API works against Azurite on a laptop. Before it goes to Azure, the infrastructure review asks for five changes:

1. Geo-redundant storage in production only.
2. No anonymous blob access.
3. An `application` tag on the storage account.
4. Blob access for the API, and nothing else in the account.
5. A cap of three API replicas.

None of these are API settings. `api.WithEnvironment("Storage__Sku", "Standard_LRS")` would only hand the API a string. They're properties of the Azure resources Aspire generates, so they belong in the AppHost.

## Start from what Aspire generates

```csharp
var storage = builder.AddAzureStorage("storage")
    .RunAsEmulator();

var uploads = storage.AddBlobContainer("uploads");

builder.AddAzureContainerAppEnvironment("aca");

var api = builder.AddProject<Projects.Api>("api")
    .WithReference(uploads)
    .WaitFor(uploads);
```

These fragments need the `Aspire.Hosting.Azure.Storage` and `Aspire.Hosting.Azure.AppContainers` packages and go before `builder.Build().Run()`.

There are no mode checks. `RunAsEmulator` only applies to a local run, so `aspire run` gets Azurite and `aspire publish` generates an Azure Storage account.[^storage] The Container Apps environment works the other way: it's only added to the model when publishing.[^aca]

Run `aspire publish` before changing anything and read the output. These are the 13.6.1 defaults behind the five requests:

| Review request                 | Aspire 13.6.1 default                   | Where to change it           |
| ------------------------------ | --------------------------------------- | ---------------------------- |
| Production-only geo-redundancy | `Standard_GRS` in every environment     | `ConfigureInfrastructure`    |
| No anonymous blob access       | `allowBlobPublicAccess` not set         | `ConfigureInfrastructure`    |
| Application tag                | Only `aspire-resource-name`             | `ConfigureInfrastructure`    |
| Blob-only access for the API   | Blob, Table, and Queue Data Contributor | `WithRoleAssignments`        |
| Three-replica cap              | `minReplicas: 1`, no maximum            | `PublishAsAzureContainerApp` |

The account also requires TLS 1.2 and disables shared-key access by default, so the examples don't repeat those settings.

## Change the storage account

`ConfigureInfrastructure` gives you the provisioning model Aspire built for the resource before it becomes Bicep:[^customize]

```csharp
using Azure.Provisioning.Storage;
using Microsoft.Extensions.Hosting;

storage.ConfigureInfrastructure(infrastructure =>
{
    var account = infrastructure.GetProvisionableResources()
        .OfType<StorageAccount>()
        .Single();

    account.Sku = new StorageSku
    {
        Name = builder.Environment.IsProduction()
            ? StorageSkuName.StandardGrs
            : StorageSkuName.StandardLrs
    };
    account.AllowBlobPublicAccess = false;
    account.Tags["application"] = "uploads";
});
```

The `using` directives go at the top of the AppHost file. `Single()` expects exactly one storage account in this resource's model. If that ever changes, publishing fails instead of customizing the wrong account.

The SKU follows the AppHost environment, which `aspire publish` sets to `Production` unless you pass `--environment`. Publishing with `--environment Staging` produced:

```bicep
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    isHnsEnabled: false
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
  tags: {
    'aspire-resource-name': 'storage'
    application: 'uploads'
  }
```

Look at `networkAcls`. Blocking anonymous blob access doesn't make the account private; its network rule still allows public traffic. Private networking is a separate change. In 13.6.1, giving the account a private endpoint switches that default to `Deny`.

Don't wrap this callback in an `IsPublishMode` check. If a developer drops the emulator and runs against Azure Storage, Aspire provisions their account from the same callback.[^provisioning] A Publish-only guard would give them the defaults instead.

## Narrow the API's access

By default, the API's reference grants its managed identity three data roles on the account. Replace them with the one it needs:[^roles]

```csharp
api.WithRoleAssignments(storage, StorageBuiltInRole.StorageBlobDataContributor);
```

`WithRoleAssignments` replaces the defaults for this resource instead of adding to them. The generated `api-roles-storage` module went from three role assignments to one.

These roles control what the running API can do. The identity that runs the deployment needs its own permissions.

## Customize the container app

The API's compute resource has its own hook:

```csharp
api.PublishAsAzureContainerApp((infrastructure, app) =>
{
    app.Template.Scale.MaxReplicas = 3;
});
```

```bicep
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
```

This hook only runs when publishing. During a local run, the call returns without changing anything.[^aca] The storage callback is different: it applies wherever Aspire provisions the account.

## When the platform team owns the account

If the storage account already exists, reference it instead of creating one:

```csharp
storage.AsExisting(
    builder.AddParameter("storageName"),
    builder.AddParameter("storageResourceGroup"));
```

Use `RunAsExisting` or `PublishAsExisting` to do this in only one mode. The generated Bicep declares the account as `existing` but still declares the `uploads` container inside it, so the deployment needs permission to create that container.

The account's own properties are no longer the AppHost's to set. With `AsExisting`, the callback above fails during publishing with `Cannot assign to output value AllowBlobPublicAccess`. Take SKU and access-policy requests to the account's owner.

## Review the Bicep, change the AppHost

Because `aspire publish` writes the Bicep, each change above shows up as a diff you can review. If a reviewer wants something different, change the AppHost and publish again. The next publish regenerates the Bicep from the AppHost, so edits made only to the generated files don't last.

The Bicep shows what will be declared. It doesn't show that Azure accepted the deployment or that the access rules work. After an authorized deployment, upload a file as the API and confirm that a caller without the role is rejected.

None of the five changes touched the API's code or configuration. They're in the AppHost, next to the resources they change.

[^storage]: The [13.6.1 Azure Storage integration](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting.Azure.Storage/AzureStorageExtensions.cs) defines the account defaults, the default role assignments, and the `RunAsEmulator` behavior.

[^aca]: In 13.6.1, the [Container Apps environment](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting.Azure.AppContainers/AzureContainerAppExtensions.cs) is only added to the model when publishing, and [`PublishAsAzureContainerApp`](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting.Azure.AppContainers/AzureContainerAppProjectExtensions.cs) returns early outside Publish mode.

[^customize]: [Customize Azure resources](https://aspire.dev/integrations/cloud/azure/customize-resources/) covers `ConfigureInfrastructure` and existing resources.

[^provisioning]: In 13.6.1, the [run-mode Bicep provisioner](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting.Azure/Provisioning/Provisioners/BicepProvisioner.cs) renders each resource through [`GetBicepTemplateFile`](https://github.com/microsoft/aspire/blob/v13.6.1/src/Aspire.Hosting.Azure/AzureProvisioningResource.cs), which applies its infrastructure callbacks.

[^roles]: [Manage Azure role assignments](https://aspire.dev/integrations/cloud/azure/role-assignments/) explains default and explicit role assignments.
