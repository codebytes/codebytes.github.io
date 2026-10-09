---
title: "Same AppHost, Different Deployment Promises"
draft: true
date: "2026-10-07T09:05:00-04:00"
lastmod: "2026-10-08T23:04:45-04:00"
categories:
  - "Development"
tags:
  - "Aspire"
  - "Azure"
  - "Deployment"
  - "Kubernetes"
  - "Containers"
series:
  - "Aspire Field Notes"
series_order: 6
permalink: "/posts/aspire-field-notes-choose-your-deployment/"
slug: "aspire-field-notes-choose-your-deployment"
image: "featured.png"
featureImage: "featured.png"
header:
  teaser: "featured.png"
  og_image: "featured.png"
excerpt_separator: "<!--more-->"
description: "Inspect the catalog's generated Compose files, then compare Container Apps, Express, Sandboxes, and Kubernetes against the application's storage and networking needs."
---

The catalog application works locally. Its references resolve, the database is ready, and we can follow a request through the dashboard. What will change when we publish it?

The API still needs its database and inventory service. The frontend still calls `/api/catalog`. But the local proxy, file paths, credentials, and open ports all need a deployment-specific arrangement.

<!--more-->

For this final part of [Aspire Field Notes](/series/aspire-field-notes/), we'll inspect the catalog's Compose output first, then look at where the cloud targets differ. My [deployment and pipelines article](/posts/aspire-cli-part-2/) covers the CLI commands in more detail.

## Read the Compose output before running it

The companion publishes **Docker Compose** artifacts for review. It does not build container images, run `docker compose up`, or provision Azure resources. The cloud targets later in this post are comparisons with their documentation.

[Walkthrough 06](https://github.com/codebytes/blog-samples/tree/main/aspire-field-notes/walkthroughs/06-choose-your-deployment) has the exact commands. Stop the running catalog AppHost, then publish with `Deployment__Target=compose`. In publish mode, this AppHost rejects a missing or unsupported target.

`aspire publish --list-steps` lists the planned pipeline without executing its steps, though it still prepares and evaluates the AppHost. A real publish reports each step it executed:

{{< figure src="publish-summary.png" alt="Terminal output from aspire publish with Deployment__Target=compose: 8 of 8 steps succeeded, a step timeline from validate-compute-environments through publish-compose, and Pipeline succeeded" caption="All eight publishing steps completed. The next step is to inspect what they generated." figureClass="full-width" >}}

Publishing can build code or invoke tools through registered pipeline steps. Check any custom steps before running it; it isn't necessarily a passive file-generation operation.[^publish]

Open `artifacts/compose/docker-compose.yaml`, `.env`, and the generated `web.Dockerfile`. The companion's `review-compose.mjs` script parses Compose configuration without interpolation and checks that:

- `api`, `inventory`, `postgres`, and `web` are present.
- The API has database and inventory references.
- `DATA_PATH` is `/data`, with the named `catalog-state` volume mounted there.
- The frontend's `/api/{**catch-all}` route preserves the `/api` prefix.
- Only the frontend and optional dashboard expose host ports.
- The intentional fault is disabled, and the database password is represented by a secret placeholder.

These fields from a completed `review.json` show the storage and route checks in a more readable form:

```json
{
  "apiDataPath": "/data",
  "stateVolume": {
    "read_only": false,
    "source": "catalog-state",
    "target": "/data",
    "type": "volume"
  },
  "proxyPath": "/api/{**catch-all}",
  "deployed": false
}
```

The full result also records the Compose file's SHA-256 and contains no secret values. The script removes an earlier `review.json` before checking and writes a replacement only after every assertion passes. That prevents an old passing result from sitting beside newly generated files. It leaves credentials and deployment-specific image placeholders unresolved.

The frontend configuration explains why `/api/catalog` survives the move from Vite to a published container:

```csharp
#pragma warning disable ASPIREJAVASCRIPT001 // PublishAsStaticWebsite is still experimental in 13.6.
web.PublishAsStaticWebsite("/api", api, options => options.StripPrefix = false);
#pragma warning restore ASPIREJAVASCRIPT001
```

`PublishAsStaticWebsite` dates from 13.3 and is still experimental in 13.6. It generates a static-site and YARP publishing model. `StripPrefix` defaults to `false`; the companion sets it explicitly so `/api/catalog` reaches the API unchanged. With `true`, the API would receive `/catalog`, which isn't its route. Vite's development proxy is no longer involved.

Read the generated image references too. With 13.6.1, `web.Dockerfile` builds on `node:22-slim` and serves the frontend from `mcr.microsoft.com/dotnet/nightly/yarp:2.3-preview`. The Compose dashboard uses `mcr.microsoft.com/dotnet/nightly/aspire-dashboard:13.6`. Review those preview and nightly images against your image policy before deploying.

## Choose a target from the application's requirements

Compose gives us files to inspect, but choosing a production target needs a few more answers:

- Does the API need private access to other services?
- Which data must survive a restart, redeploy, or failed node?
- Can the frontend and API tolerate cold starts?
- Which identity calls the database or secret store?
- Who owns capacity, upgrades, ingress, and incident response?
- Are preview services and packages acceptable for this workload?

Those answers narrow the choice:

| Target or mode                   | Good reason to evaluate it                                               | Question to resolve first                                                       |
| -------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| Docker Compose                   | Validate the app's container behavior on a known host                    | Who owns that host, its storage, backups, and exposure?                         |
| Regular Azure Container Apps     | Use a managed application platform without owning a Kubernetes cluster   | Do its networking, storage, scaling, and identity choices fit this application? |
| Kubernetes or AKS                | Use cluster capabilities and policies your organization already operates | Is the team prepared to own the corresponding cluster complexity?               |
| Container Apps Express preview   | Explore a smaller environment model for suitable HTTP workloads          | Can the app accept its public-endpoint and feature constraints?                 |
| Container Apps Sandboxes preview | Explore isolated sandbox execution and lifecycle policies                | Does the workload fit the currently narrow supported surface?                   |

For any target, review generated routing, environment-variable names, mounts, secret references, and images. The two new Container Apps options deserve particular care because their defaults differ from regular Container Apps.

## Check Express networking and defaults

The `AsExpress()` API is experimental, reports `ASPIREACAEXPRESS001`, and selects the Container Apps Express preview environment type.[^express]

The changes include:

- Minimum replicas default to zero when you have not specified them, so cold starts are part of the workload's behavior.
- The environment does not include the managed Aspire Dashboard.
- Aspire omits automatic .NET data-protection configuration.
- Referenced endpoints must be explicitly public; there is no private `.internal` hostname for this reference path.
- HTTPS ingress is required.

The local dashboard still works, which can make the missing managed dashboard easy to overlook. Private service discovery also needs attention before selecting this target.

`WithExternalHttpEndpoints()` exposes an endpoint; it does not add application authentication or authorization. If publishing rejects an internal reference, making it public changes who can reach the service. Review that access before changing the endpoint.

If the app relies on protected cookies or other .NET data-protection behavior, plan its configuration explicitly as well.

## Sandboxes have different access and storage limits

Azure Container Apps Sandboxes is a preview Azure service, and `Aspire.Hosting.Azure.Sandboxes` is a prerelease package. You need preview access in the target subscription and region.[^sandboxes]

The companion has no Sandbox deployment AppHost. The [official setup](https://aspire.dev/deployment/azure/sandboxes/) adds a sandbox group and suitable container-backed compute resources. Try it separately if its constraints fit your workload.

A local run does not provision Azure sandboxes. Published Bicep describes the infrastructure; the deployment workflow creates sandboxes, disk images, ports, and URLs. Deployment requires permissions for the group, registry, identities, and scoped role assignments. Review that plan and its costs before authorizing it.

Only external endpoints receive public HTTPS URLs. Sandbox endpoints require Microsoft Entra ID authentication by default unless a specific endpoint opts into anonymous access. Egress is deny-by-default. Unlike Express, this target does supply default endpoint authentication.

The current integration excludes volumes and container mounts, TCP ports, private service discovery, and endpoint references across sandbox groups. Images must provide a Linux/amd64 manifest; Windows and ARM64 images are not supported.

We therefore can't move the catalog's PostgreSQL container and volume over unchanged. The portable path from [part five](/posts/aspire-field-notes-portable-state-and-config/) doesn't supply storage on a target that lacks mounts.

Also distinguish the deployment, image-pull, and workload identities. An identity that can pull an image doesn't necessarily have permission to query the database.

## What 13.6 improves for an existing deployment

The new preview targets are only part of the release. Existing Kubernetes and Azure workflows also get useful corrections:[^release]

- Routes without an explicit hostname can inherit the configured hostname rather than losing it.
- Helm values retain parameters embedded in environment expressions.
- AKS environments can provision persistent-volume resources.
- Deployment state is scoped beneath `ASPIRE_HOME`, including separate identities for sibling single-file AppHosts.

Compare the generated output before and after upgrading, especially where you've worked around an older behavior.

## Review migrations before rollout

Use a branch and keep the prior known-good deployment artifacts available. The release has several changes that deserve conditional checks:

| If the application uses...           | Review before rollout                                                                                         |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Custom connection-string readers     | The portable aliases and lookup behavior described in part five                                               |
| Local MongoDB or Cosmos DB emulators | TLS expectations, changed emulator defaults, and re-seeding requirements                                      |
| Azure Front Door                     | Changed origin naming and whether old origins need explicit cleanup after confirming the new ones are healthy |
| Prerelease .NET Project V2           | Restore hooks, custom `ProjectResource` integrations, and Rebuild versus Restart behavior                     |
| GitHub Models                        | The retired service and the migration to a supported integration                                              |

The GitHub Models service was retired on July 30, 2026; Aspire deprecated its hosting integration in 13.5 and removed its source from the repository in 13.6. An old provider-selection example is not evidence that the service remains available.[^models]

An upgrade is not permission to delete old Front Door origins or recreate a location-immutable resource automatically. Review the live resources, confirm replacements, and approve any destructive cleanup separately.

## Make the release gate an application check

The companion stops at artifact review. The following are requirements for a subsequent real deployment, not outcomes claimed by the publish-only walkthrough.

For your selected target, verify the same kind of operation we used to begin the series:

1. The intended request succeeds using the deployed route and identity.
2. A caller without permission is rejected where access is required.
3. The application's data survives the lifecycle it is supposed to survive.
4. A controlled dependency failure produces a useful, bounded response.
5. Production telemetry reaches the intended backend rather than relying on a developer's local dashboard.

Measure cold starts, scale, or concurrency in the deployed environment when they matter to the workload.

The series started with `GET /api/catalog` failing while every service looked healthy. Keep that request in the deployment checks too. A completed publish is useful progress; the deployed route, identity, and dependencies still need to handle the request together.

[^express]: [Container Apps Express behavior, limitations, and experimental diagnostic](https://aspire.dev/deployment/azure/container-apps/#express-environments).

[^sandboxes]: [Sandboxes prerequisites, identities, publishing, deployment, and limitations](https://aspire.dev/deployment/azure/sandboxes/).

[^publish]: [`aspire publish` pipeline and command options](https://aspire.dev/reference/cli/commands/aspire-publish/).

[^release]: [Aspire 13.6 deployment changes and migration guidance](https://aspire.dev/whats-new/aspire-13-6/).

[^models]: [GitHub Models retirement](https://github.blog/changelog/2026-07-30-github-models-is-now-retired/) and [Aspire migration guidance](https://aspire.dev/integrations/ai/github-models/github-models-get-started/).
