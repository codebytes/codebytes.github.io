---
title: "One Configuration Contract, From Laptop to Container"
draft: false
date: "2026-11-23T20:38:00-05:00"
categories:
  - "Development"
tags:
  - "Aspire"
  - "Configuration"
  - "Containers"
  - "Storage"
  - "Security"
series:
  - "Aspire Field Notes"
series_order: 5
permalink: "/posts/aspire-field-notes-portable-state-and-config/"
slug: "aspire-field-notes-portable-state-and-config"
image: "featured.png"
featureImage: "featured.png"
header:
  teaser: "featured.png"
  og_image: "featured.png"
excerpt_separator: "<!--more-->"
description: "Save a catalog note, restart the API, and prove the same note survived. Use Aspire 17 to give the API one storage setting on your laptop and in Docker Compose."
---

Save a note in the catalog and read it back. You get `200 OK`, but you still don't know whether a new API process can find that note. For that, you need two responses with different instance IDs and the same saved data.

<!--more-->

For part five of [Aspire Field Notes](/series/aspire-field-notes/), the catalog moves to **Aspire 17.0.0**. The API still asks for one setting, `DATA_PATH`. Locally it needs a directory on your laptop. In Docker Compose it needs a mount inside the container. The AppHost can supply both without changing the API.

## Let the AppHost choose the path

Earlier parts used `AddProject` to register the .NET services. In Aspire 17 that method is obsolete. The [upgraded AppHost][apphost] uses `Microsoft.NET.Sdk` with the `Aspire.Hosting.AppHost` and `Aspire.Hosting.Dotnet` packages. It registers each service by passing its `.csproj` path to `AddDotnetProject`. Updating the CLI alone wouldn't change those project files.[^upgrade]

The volume setting already existed in 13.6. Here's the configuration that carries over to the new `api` resource:

```csharp
api.WithEnvironment("Catalog__Region", region)
    .WithVolume("catalog-state", "/data", env: "DATA_PATH");
```

`Catalog__Region` passes a value the API reads as `Catalog:Region`. `WithVolume` does two things: it declares the storage and tells Aspire which environment variable should hold its path.[^volumes]

| Where the API runs        | What `DATA_PATH` points to                                 |
| ------------------------- | ---------------------------------------------------------- |
| Local .NET process        | A directory for this workload in the AppHost's local store |
| Published Compose service | `/data` inside the API container, backed by a named volume |

On a local run, look under `catalog/Catalog.AppHost/obj/.aspire/volumes/` for `state.json`. Aspire picks the subdirectory for the workload and volume. A normal restart leaves it alone; deleting the AppHost's `obj` directory also deletes the note.

The API reads the same key in both places:

```csharp
var state = new StateStore(builder.Configuration.Require("DATA_PATH"));
```

`StateStore` rejects a relative path, creates the directory if needed, and keeps the note in `state.json`. If an existing file is corrupt, startup fails instead of replacing the note with an empty one. Publishing the app doesn't copy your laptop's `state.json` into the container.

## Save a note and restart the catalog

[Download the catalog revision used here][sample-zip] and open its `aspire-field-notes` directory. The [Part 5 walkthrough][walkthrough] links to the prerequisites: Aspire CLI 17.0.0, a .NET 10 SDK, Node.js, and a running container engine. Start the catalog in Bash or PowerShell:

```bash
node scripts/init-secret.mjs
aspire start --apphost catalog --isolated
aspire wait web --apphost catalog
node scripts/state-smoke.mjs write
```

The helper writes a fresh note through the frontend's `/api/state` route, reads it back, and saves the response for comparison. It also sends a blank note. The API must return `400` and leave the saved note alone.

In the same shell, stop and start the same AppHost. Leave its storage in place:

```bash
aspire stop --apphost catalog
aspire start --apphost catalog --isolated
aspire wait web --apphost catalog
node scripts/state-smoke.mjs verify
```

The API generates an `instanceId` at startup. On Windows with Docker and .NET SDK 10.0.404, the ID started with `e6472b25` before the restart and `7fd26907` afterward. Both responses had revision `1`, the same message, and the same `updatedUtc`. Running `verify` before the restart failed: an unchanged note from the same process doesn't count.

You can also read the note in the frontend:

{{< figure src="retained-note.png" alt="Catalog frontend showing an API instance ID and the saved message 'Saved before the restart' at revision 5." caption="In this earlier catalog run, Read saved note returned revision 5. The restart check compares the instance ID and state with the original response." figureClass="full-width" >}}

## Check what Compose will mount

After checking the note, stop this AppHost and generate the Compose files:

```bash
aspire stop --apphost catalog
aspire publish --apphost catalog -o artifacts/compose -- --Deployment:Target=compose
```

Once publication succeeds, run `node scripts/review-compose.mjs artifacts/compose`. In the generated `docker-compose.yaml`, the `api` service has `DATA_PATH=/data` and a writable mount from the named volume `catalog-state` to `/data`. Check both. With just the environment variable, the API could write to the container's own filesystem and lose the note when the container is replaced.

This command inspects deployment files. It doesn't start the Compose stack or prove that a deployed volume can be restored from backup. The catalog also serializes file writes within one API process. If two replicas need to update the same note, use storage that coordinates their writes.

## Keep the database password stable across restarts

The note and PostgreSQL use different storage. You can retain both and still lose database access: keeping the PostgreSQL volume preserves the password already set inside it. Setting a different AppHost secret on the next run doesn't rotate that password.

The setup helper keeps an existing `postgres-password` and creates one outside Git only when it's missing. The AppHost passes the database connection through `WithReference(catalogdb)`; the API opens it with `AddNpgsqlDataSource("catalogdb")`. If you need to rotate the password, change the database credential and its consumers together.

`catalogdb` has another useful property: its name is already valid in an environment variable. A name such as `catalog-db` gets a portable alias, `ConnectionStrings__catalog_db`, for stricter publishers. Aspire's client integrations know to try that alias. A direct `.GetConnectionString("catalog-db")` call doesn't translate the name for you.[^names]

{{< figure src="parameters-masked.png" alt="The Aspire 13.6 dashboard shows the public catalog region as local and masks the PostgreSQL password." caption="This is the 13.6 dashboard from the earlier walkthroughs. Masking a parameter on screen doesn't redact it from saved dashboard data." figureClass="full-width" >}}

Before relying on a deployment, repeat the note test there with disposable data. Replace the API container, then read the note from the replacement. A new instance ID with the original revision tells you something a green health check can't.

{{% if-published "/posts/aspire-field-notes-choose-your-deployment" %}}
[Next: choose a deployment target that can honor those expectations](/posts/aspire-field-notes-choose-your-deployment/).
{{% /if-published %}}

[apphost]: https://github.com/codebytes/blog-samples/blob/6c7c7425ca347e20934f0e9d840a1edbabf98eb9/aspire-field-notes/catalog/Catalog.AppHost/Catalog.AppHost.csproj
[sample-zip]: https://github.com/codebytes/blog-samples/archive/6c7c7425ca347e20934f0e9d840a1edbabf98eb9.zip
[walkthrough]: https://github.com/codebytes/blog-samples/tree/6c7c7425ca347e20934f0e9d840a1edbabf98eb9/aspire-field-notes/walkthroughs/05-portable-state-and-config

[^upgrade]: [What's new in Aspire 17.0](https://aspire.dev/whats-new/aspire-17/) and [migrating .NET project resources](https://aspire.dev/integrations/dotnet/migrate-dotnet-project-resource/).

[^volumes]: [Portable volume paths and persistent database credentials](https://aspire.dev/fundamentals/persist-data-volumes/).

[^names]: [How Aspire maps logical connection names to environment variables](https://aspire.dev/fundamentals/environment-variables/#connection-strings).
