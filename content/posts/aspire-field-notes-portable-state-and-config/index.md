---
title: "One Configuration Contract, From Laptop to Container"
date: "2026-10-06"
draft: true
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
header:
  teaser: ""
  og_image: ""
excerpt_separator: "<!--more-->"
description: "Use Aspire 13.6's portable volume paths and connection-string aliases while keeping configuration, credentials, and persistent state as separate responsibilities."
---

The application writes files to a development directory on your laptop and `/data` in a container. Somewhere in the code, an environment check chooses between them. A second check chooses a connection-string key. A third compensates for a certificate difference.

Each workaround is small. Together, they make "works locally" a poor predictor of "works after publishing."

<!--more-->

In part five of [Aspire Field Notes](/series/aspire-field-notes/), the goal is a stable application-facing contract. Aspire can translate that contract into target-specific configuration without pretending every environment has identical storage, networking, or permissions.

The [portable-state companion exercise](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/exercises/05-portable-state-and-config) uses the shared catalog app's `GET /api/state` and `POST /api/state` endpoints. Follow the exercise's request payload and restart sequence to write a disposable JSON record, restart without deleting storage, and check that the same value remains.

Run its commands from the sample checkout's `aspire-field-notes/` directory. The state endpoint is a local teaching surface, not a production API or a substitute for access controls.

## Give the application a setting, not a platform detector

The catalog companion stores that JSON record beneath `DATA_PATH`. The API reads the setting rather than inferring whether it is running under Docker. The same pattern can apply to an image cache or another application-owned directory, with different durability requirements.

Aspire 13.6 adds an `env` argument to volume mounts on projects and executables. The companion's `api` resource already declares it in the chain shown in [part two](/posts/aspire-field-notes-model-the-whole-app/):

```csharp
    .WithVolume("catalog-state", "/data", env: "DATA_PATH")
```

In local process execution, `DATA_PATH` identifies a deterministic, workload-scoped directory in the AppHost's local store. In a published container, it identifies the configured mount path, `/data`.[^volumes]

For the companion, that local store is under `catalog/Catalog.AppHost/obj/.aspire/volumes/`. Deleting the `obj` folder or running `git clean -fdX` removes the saved note along with other build output.

The application code does not need a special container branch. The companion's API reads the value through a small `Require` configuration helper, and its `StateStore` constructor rejects a relative path and creates the directory. A minimal equivalent is:

```csharp
var dataPath = builder.Configuration["DATA_PATH"]
    ?? throw new InvalidOperationException("DATA_PATH must be configured.");

if (!Path.IsPathFullyQualified(dataPath))
{
    throw new InvalidOperationException("DATA_PATH must be an absolute path.");
}

Directory.CreateDirectory(dataPath);
```

This pattern belongs in the .NET API's startup code, not the AppHost. A missing setting or inaccessible directory should fail visibly rather than silently redirect data to a temporary folder.

The `env` argument targets projects and executables, whose run-mode path is computed on the host. Containers always see the target path: in C#, the overload also compiles for a container and simply sets the variable to that target, while TypeScript AppHosts expose `env` only for projects and executables.

## Prove that the value survived a real restart

After collection setup, use a healthy catalog run. If you have a previous run active, stop only that sample's AppHost first:

```bash
apphost=catalog/Catalog.AppHost/Catalog.AppHost.csproj
Inventory__FaultEnabled=false bash scripts/aspire.sh start \
  --apphost "$apphost" --isolated --non-interactive &&
node scripts/smoke.mjs healthy &&
node scripts/state-smoke.mjs write

bash scripts/aspire.sh stop --apphost "$apphost" --non-interactive &&
Inventory__FaultEnabled=false bash scripts/aspire.sh start \
  --apphost "$apphost" --isolated --non-interactive &&
node scripts/smoke.mjs healthy &&
node scripts/state-smoke.mjs verify
```

The write check posts a fresh note, reads it back, and confirms that a rejected blank write does not mutate the saved state. The verification requires a **different API instance ID** but the **same note, revision, and timestamp**. Running verification without restarting is intentionally a failure.

The frontend's **Save note** action sends a payload such as:

```json
{
  "message": "Retained after a restart"
}
```

Messages must be non-blank and no longer than 256 characters. The API stores `state.json` beneath `DATA_PATH`; the helper stores its expected result separately in ignored `artifacts/state-check.json`.

Writes are serialized within one API process and replace the file atomically. This is a teaching example for a single writer, not a claim of coordination between multiple replicas.

## A portable path is not portable durability

The same `DATA_PATH` name does not give a laptop directory, a Docker volume, and a cloud-mounted share identical behavior.

Before making the cache contain irreplaceable data, decide:

- Who owns the backing storage and its lifecycle?
- Can multiple replicas write safely?
- What permissions does the application identity have?
- What are the capacity, backup, and restore requirements?
- Does the selected deployment target support this mount at all?

For AKS, a persistent volume requires the appropriate storage class, access mode, and capacity. A bind mount on a developer machine does not answer those questions.

For a cache, losing files may be acceptable because the application can reconstruct them. For uploaded documents or a database, that same behavior would be data loss. The API convenience should not erase the distinction.

## There are several kinds of state

It helps to name them separately:

| State                          | Purpose                                 | What retaining it does not retain                       |
| ------------------------------ | --------------------------------------- | ------------------------------------------------------- |
| Dashboard database             | Diagnostic runs and telemetry           | The application's database or uploaded files            |
| Application volume or database | Workload data                           | A reproducible record of every diagnostic run           |
| Deployment state               | Information used to manage a deployment | A backup of application data or an authorization policy |

Pinning a dashboard run does not preserve the PostgreSQL volume. Keeping a database volume does not preserve the logs you forgot to capture.

The distinction also affects cleanup. The 13.6 `--volumes` option on a forced stop can remove Aspire-owned named volumes; it is an intentional destructive choice, not a routine cure for a failed startup. Review exactly which data you are retiring before using it.

## The less visible 13.6 change: connection names

The companion consumes the simple connection name `catalogdb` through .NET configuration and `Aspire.Npgsql`. The hyphenated-name discussion below is a migration note for other applications, not an alias conversion silently performed by a Node or Python client in this sample.

Existing applications often have names such as `catalog-db`.

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

Names such as `catalog-db` and `catalog_db` can collapse to the same physical alias. Aspire rejects that collision instead of silently choosing one. A startup error here is useful; a retry loop cannot repair ambiguous configuration.

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

This is the same separation as `WithReference` versus `WithEnvironment`: resource relationships supply connection information; explicit settings adapt that information to a consumer's expected contract. Neither is a reason to invent another checked-in secret file.

For application-side validation, my [earlier configuration article](/posts/dotnet-configuration/) explains the fail-at-startup pattern. The new problem here is keeping that validated contract consistent across publishers.

## Persist credentials deliberately when data persists

A database volume can retain credentials initialized during an earlier run. If the AppHost supplies a different generated password on the next run, keeping the data and changing the credential can produce an authentication failure.

Use the integration's documented secret-parameter mechanism and a local secret store to keep the intended value stable. When rotating it, update the actual database credential and its consumers together; changing an environment variable alone is not a database password-rotation procedure.[^volumes]

Outside local development, prefer workload identity and a managed secret service where the chosen integration supports them. Supplying an endpoint or connection reference is not granting a cloud role.

Also remember the diagnostic boundary from [part one](/posts/aspire-field-notes-keep-the-failing-run/): values masked in the dashboard can still exist unredacted in persisted data. "Not visible in the UI" is not equivalent to "not stored."

## Two upgrade changes that can look like application bugs

### MongoDB transport

In 13.6, ordinary local MongoDB resources participate in shared certificate configuration. When a certificate is available under the defaults, the server requires TLS and the generated connection string includes it.

A hand-built URI based only on host and port can miss that configuration. Use the complete generated connection information and verify both certificate trust and hostname matching. Trusting a certificate alone does not fix connecting through a name it does not cover.

Do not turn off certificate validation simply to get back to a green dashboard. Diagnose the transport contract first.

### Cosmos DB emulator data

`RunAsEmulator` now selects the Linux-based vNext emulator. Its data path differs from the classic emulator, and existing classic data does not carry over automatically.

For an intentional migration, plan to re-seed the emulator and review unsupported options such as partition-count configuration. If you need the previous emulator, the documented compatibility path is `RunAsClassicEmulator`.[^release]

Neither change is a generic transient failure. More retries or a longer startup delay will not migrate data or repair a TLS mismatch.

## Prove the contract before deploying

Run a small check in both the local and intended container environments:

1. Confirm the required settings are present without printing secrets.
2. Write disposable test data through the application's normal path.
3. Restart using the lifecycle you intend to support and check the expected retention.
4. Confirm the database connection uses the intended name and transport.
5. Remove or rename a required setting and verify that startup fails clearly.

The desired result is not identical physical paths. It is identical application expectations, with storage and security differences made explicit.

[Next: choose a deployment target that can honor those expectations](/posts/aspire-field-notes-choose-your-deployment/).

[^volumes]: [Portable volume paths, data retention, and persistent credentials](https://aspire.dev/fundamentals/persist-data-volumes/).

[^environment]: [Logical connection names, portable aliases, lookup rules, and collisions](https://aspire.dev/fundamentals/environment-variables/).

[^release]: [Aspire 13.6 configuration, MongoDB TLS, and Cosmos DB emulator migration notes](https://aspire.dev/whats-new/aspire-13-6/).
