---
title: "One Configuration Contract, From Laptop to Container"
date: "2026-10-07T09:04:00-04:00"
lastmod: "2026-10-08T23:04:45-04:00"
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
description: "Give the API one DATA_PATH setting on the host and in a container, check that a saved note survives restart, and handle Aspire 13.6's connection-name changes."
---

The application writes files to a development directory on your laptop and `/data` in a container. Somewhere in the code, an environment check chooses between them. A second check chooses a connection-string key. A third compensates for a certificate difference.

Soon the application knows quite a bit about the machine it's running on, just to find its own files and database.

<!--more-->

For part five of [Aspire Field Notes](/series/aspire-field-notes/), we'll move the path choice into the AppHost and have the API read one setting. Then we'll look at the storage and credential differences that still need attention.

## Give the application a setting, not a platform detector

The catalog companion stores a small JSON record beneath `DATA_PATH`. The API reads that setting without checking whether it's running under Docker. You could use the same pattern for an image cache or another application-owned directory.

Aspire 13.6 adds an `env` argument to volume mounts on projects and executables. The companion's `api` resource already declares it in the chain shown in [part two](/posts/aspire-field-notes-model-the-whole-app/):

```csharp
    .WithVolume("catalog-state", "/data", env: "DATA_PATH")
```

In local process execution, `DATA_PATH` identifies a deterministic, workload-scoped directory in the AppHost's local store. In a published container, it identifies the configured mount path, `/data`.[^volumes]

For the companion, that local store is under `catalog/Catalog.AppHost/obj/.aspire/volumes/`. Deleting the `obj` folder or running `git clean -fdX` removes the saved note along with other build output.

The companion's API reads the value through a small `Require` configuration helper. Its `StateStore` constructor rejects relative paths and creates the directory. The essential startup check looks like this:

```csharp
var dataPath = builder.Configuration["DATA_PATH"]
    ?? throw new InvalidOperationException("DATA_PATH must be configured.");

if (!Path.IsPathFullyQualified(dataPath))
{
    throw new InvalidOperationException("DATA_PATH must be an absolute path.");
}

Directory.CreateDirectory(dataPath);
```

This belongs in the .NET API's startup code. If the setting is missing or the directory is inaccessible, startup should fail with that error. Falling back to a temporary folder would make the app appear to work until its data disappeared.

The `env` argument targets projects and executables, whose run-mode path is computed on the host. Containers always see the target path: in C#, the overload also compiles for a container and simply sets the variable to that target, while TypeScript AppHosts expose `env` only for projects and executables.

## Prove that the value survived a real restart

The catalog app's `/api/state` endpoints let us try this with a disposable note. They are for local learning and have no production access controls. Follow [walkthrough 05](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/05-portable-state-and-config) to save a note, restart without deleting storage, and read it back.

Compare both responses: `instanceId` must change, while the saved `message`, `revision`, and `updatedUtc` must stay the same. Here's the post-restart response:

{{< figure src="retained-note.png" alt="The companion frontend after a restart: State read from application storage, with a new API instance ID and the same message, revision 5, and update timestamp saved before the restart" caption="Read the saved note after restart. Compare its state with the first response and check that the API instance ID changed." figureClass="full-width" >}}

The walkthrough's `state-smoke.mjs` helper makes those comparisons automatically. Reading the note twice from the same process fails its restart check. It also checks that a rejected blank write leaves the saved state unchanged; valid messages are non-blank and at most 256 characters.

Writes are serialized within one API process and replace the file atomically. Multiple replicas would need a different coordination strategy.

## A portable path is not portable durability

The same `DATA_PATH` name does not give a laptop directory, a Docker volume, and a cloud-mounted share identical behavior.

Before storing data you can't recreate, decide:

- Who owns the backing storage and its lifecycle?
- Can multiple replicas write safely?
- What permissions does the application identity have?
- What are the capacity, backup, and restore requirements?
- Does the selected deployment target support this mount at all?

For AKS, a persistent volume requires the appropriate storage class, access mode, and capacity. A bind mount on a developer machine does not answer those questions.

Losing a rebuildable cache may be acceptable. Losing uploaded documents or a database usually isn't, even if both use the same volume API.

## There are several kinds of state

It helps to name them separately:

| State                          | Purpose                                 | What retaining it does not retain                       |
| ------------------------------ | --------------------------------------- | ------------------------------------------------------- |
| Dashboard database             | Diagnostic runs and telemetry           | The application's database or uploaded files            |
| Application volume or database | Workload data                           | A reproducible record of every diagnostic run           |
| Deployment state               | Information used to manage a deployment | A backup of application data or an authorization policy |

Pinning a dashboard run does not preserve the PostgreSQL volume. Keeping a database volume does not preserve the logs you forgot to capture.

The distinction also affects cleanup. The 13.6 `--volumes` option on a forced stop can remove Aspire-owned named volumes. Check which data will be deleted before using it to troubleshoot a startup failure.

## The less visible 13.6 change: connection names

The companion uses `catalogdb` through .NET configuration and `Aspire.Npgsql`. If your application instead has a connection name such as `catalog-db`, there's an additional 13.6 behavior to account for.

In 13.6, a logical name containing a hyphen, or any other character that isn't an ASCII letter, digit, or underscore, gets a portable environment-variable alias. Leading digits and repeated underscores are normalized too:

| Logical name | Original variable               | Portable alias                  |
| ------------ | ------------------------------- | ------------------------------- |
| `catalog-db` | `ConnectionStrings__catalog-db` | `ConnectionStrings__catalog_db` |

Targets that accept both forms can receive both. Stricter publishers, including Kubernetes-based targets, Azure App Service, and Foundry Hosted Agents, emit only the portable alias.[^environment]

Updated Aspire client integrations understand the logical lookup and its portable fallback. Update them alongside the AppHost. A custom environment-variable reader or a direct `GetConnectionString` call does not automatically acquire that behavior.

For a legacy .NET consumer with the known logical name `catalog-db`, make the lookup explicit:

```csharp
var connectionString = builder.Configuration.GetConnectionString("catalog-db")
    ?? builder.Configuration.GetConnectionString("catalog_db");

if (string.IsNullOrWhiteSpace(connectionString))
{
    throw new InvalidOperationException(
        "The catalog database connection must be configured.");
}
```

The fallback is for an absent original key, not for retrying a failed database connection. Do not log either value to explain the configuration error.

Another option is to choose an explicitly portable connection name and use it consistently in both the reference and consumer. Renaming only one side breaks the contract.

Names such as `catalog-db` and `catalog_db` can collapse to the same physical alias. Aspire rejects the collision at startup; choose distinct names to resolve it.

## Keep the two configuration layers clear

TypeScript AppHosts now load the standard configuration stack from the directory containing `apphost.mts`, including `appsettings.json` and environment-specific files.[^release]

That makes a setting such as this available to **AppHost composition code**:

```json
{
  "Catalog": {
    "EnableLocalDiagnostics": false
  }
}
```

It does not automatically send that setting to the catalog API or the browser. Consumers still receive the references and environment values the AppHost supplies.

Use `WithReference` for the resource's connection information and `WithEnvironment` for a setting the consumer expects. Keep secrets in the appropriate secret store rather than checking them into either application's configuration files.

For application-side validation, my [earlier configuration article](/posts/dotnet-configuration/) explains the fail-at-startup pattern. The new problem here is keeping that validated contract consistent across publishers.

## Persist credentials deliberately when data persists

A database volume can retain credentials initialized during an earlier run. If the AppHost supplies a different generated password on the next run, keeping the data and changing the credential can produce an authentication failure.

Use the integration's documented secret-parameter mechanism and a local secret store to keep the intended value stable. When rotating it, update the actual database credential and its consumers together; changing an environment variable alone is not a database password-rotation procedure.[^volumes]

The dashboard's **Parameters** tab shows the split in the companion: `catalog-region` is an ordinary value, while `postgres-password` is a secret parameter whose value stays masked:

{{< figure src="parameters-masked.png" alt="Aspire dashboard Parameters tab: catalog-region with the value local, and postgres-password with its value masked" caption="Catalog-region is visible; postgres-password is masked in the UI. That masking does not redact persisted dashboard data." figureClass="full-width" >}}

Outside local development, prefer workload identity and a managed secret service where the chosen integration supports them. Supplying an endpoint or connection reference is not granting a cloud role.

As [part one](/posts/aspire-field-notes-keep-the-failing-run/) explains, protect persisted dashboard data too: it can contain values that the UI masks.

## Upgrading MongoDB or the Cosmos DB emulator

### MongoDB transport

In 13.6, ordinary local MongoDB resources participate in shared certificate configuration. When a certificate is available under the defaults, the server requires TLS and the generated connection string includes it.

A hand-built URI based only on host and port can miss that configuration. Use the complete generated connection information and verify both certificate trust and hostname matching. Trusting a certificate alone does not fix connecting through a name it does not cover.

Do not turn off certificate validation simply to get back to a green dashboard. Diagnose the transport contract first.

### Cosmos DB emulator data

`RunAsEmulator` now selects the Linux-based vNext emulator. Its data path differs from the classic emulator, and existing classic data does not carry over automatically.

For an intentional migration, plan to re-seed the emulator and review unsupported options such as partition-count configuration. If you need the previous emulator, the documented compatibility path is `RunAsClassicEmulator`.[^release]

## Prove the contract before deploying

Run a small check in both the local and intended container environments:

1. Confirm the required settings are present without printing secrets.
2. Write disposable test data through the application's normal path.
3. Restart using the lifecycle you intend to support and check the expected retention.
4. Confirm the database connection uses the intended name and transport.
5. Remove or rename a required setting and verify that startup fails clearly.

The API should still read `DATA_PATH` and the intended database connection name in both environments. The AppHost handles the physical path; the deployment needs to provide storage and permissions that fit the data.

[Next: choose a deployment target that can honor those expectations](/posts/aspire-field-notes-choose-your-deployment/).

[^volumes]: [Portable volume paths, data retention, and persistent credentials](https://aspire.dev/fundamentals/persist-data-volumes/).

[^environment]: [Logical connection names, portable aliases, lookup rules, and collisions](https://aspire.dev/fundamentals/environment-variables/).

[^release]: [Aspire 13.6 configuration, MongoDB TLS, and Cosmos DB emulator migration notes](https://aspire.dev/whats-new/aspire-13-6/).
