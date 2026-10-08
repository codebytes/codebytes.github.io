---
title: "Same AppHost, Different Deployment Promises"
date: "2026-10-06"
draft: true
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
description: "Compare deployment contracts in Aspire 13.6, understand Express and Sandboxes preview boundaries, and review an upgrade before treating a local success as production readiness."
---

The catalog application works locally. Its references resolve, the database is ready, and we can follow a request through the dashboard. Now we add a deployment environment.

What should stay the same is the application's intent. What does not automatically stay the same is its networking, identity, storage, lifecycle, or operational support.

<!--more-->

This final part of [Aspire Field Notes](/series/aspire-field-notes/) is about choosing those promises deliberately. My [deployment and pipelines article](/posts/aspire-cli-part-2/) covers the command-oriented introduction; this is the 13.6 decision that comes after it.

[Walkthrough 06](https://github.com/codebytes/blog-samples/tree/codebytes-aspire-companion-samples/aspire-field-notes/walkthroughs/06-choose-your-deployment) has every command used here. It explicitly selects **Docker Compose** and publishes artifacts for review. It does not provision Azure resources or apply a cloud deployment. The cloud targets below are comparisons against their documented contracts, not additional environments quietly created by the walkthrough.

## Start with constraints, not a platform preference

For the catalog example, write down the requirements before selecting an integration:

- Does the API need private access to other services?
- Which data must survive a restart, redeploy, or failed node?
- Can the frontend and API tolerate cold starts?
- Which identity calls the database or secret store?
- Who owns capacity, upgrades, ingress, and incident response?
- Are preview services and packages acceptable for this workload?

An AppHost makes these decisions easier to express. It does not remove the decisions.

## Compare the contract you actually need

| Target or mode                   | Good reason to evaluate it                                               | Question to resolve first                                                       |
| -------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| Docker Compose                   | Validate the app's container behavior on a known host                    | Who owns that host, its storage, backups, and exposure?                         |
| Regular Azure Container Apps     | Use a managed application platform without owning a Kubernetes cluster   | Do its networking, storage, scaling, and identity choices fit this application? |
| Kubernetes or AKS                | Use cluster capabilities and policies your organization already operates | Is the team prepared to own the corresponding cluster complexity?               |
| Container Apps Express preview   | Explore a smaller environment model for suitable HTTP workloads          | Can the app accept its public-endpoint and feature constraints?                 |
| Container Apps Sandboxes preview | Explore isolated sandbox execution and lifecycle policies                | Does the workload fit the currently narrow supported surface?                   |

The last two are not spelling variations of ordinary Container Apps. They have different constraints and should not be recommended merely because they are new in 13.6.

## Express is simpler because it promises less

The `AsExpress()` API is experimental, reports `ASPIREACAEXPRESS001`, and selects the Container Apps Express preview environment type.[^express]

The changes include:

- Minimum replicas default to zero when you have not specified them, so cold starts are part of the workload's behavior.
- The environment does not include the managed Aspire Dashboard.
- Aspire omits automatic .NET data-protection configuration.
- Referenced endpoints must be explicitly public; there is no private `.internal` hostname for this reference path.
- HTTPS ingress is required.

The local dashboard still works. A local run therefore cannot demonstrate that the managed dashboard or private service discovery will exist after deployment.

Most importantly, `WithExternalHttpEndpoints()` exposes an endpoint; it does not add application authentication or authorization. Do not solve a deployment error about an internal reference by making it public without reviewing who can call it.

For an application relying on protected cookies or other data-protection behavior, treat the missing automatic configuration as a requirement to resolve, not an implementation detail to discover during a restart.

## Sandboxes are a separate experiment

Azure Container Apps Sandboxes is a preview Azure service, and `Aspire.Hosting.Azure.Sandboxes` is a prerelease package. You need preview access in the target subscription and region.[^sandboxes]

The companion does not contain a Sandbox deployment AppHost. If this target fits your requirements, use the [official Sandboxes setup](https://aspire.dev/deployment/azure/sandboxes/) in a separate, explicitly authorized experiment. It adds a sandbox group and suitable container-backed compute resources; it is not a drop-in replacement for the catalog's Compose target.

The group affects publishing and deployment; a local run does not provision Azure sandboxes. Deployment requires permissions to create the group, registry, identities, and scoped role assignments. Review the generated plan and costs before authorizing it.

Only external endpoints receive public HTTPS URLs. Sandbox endpoints require Microsoft Entra ID authentication by default unless a specific endpoint opts into anonymous access. Egress is deny-by-default.

That is different from Express, where exposing an endpoint does not supply authentication. Treating these defaults as interchangeable would be a serious design mistake.

### Check the exclusions before writing the demo

The documented Sandboxes integration does not currently support volumes or container mounts, TCP ports, private service discovery, or endpoint references across sandbox groups. Images must provide a Linux/amd64 manifest; Windows and ARM64 images are not supported.

That immediately excludes moving our catalog's local PostgreSQL container and data volume over unchanged. A working local volume setting from [part five](/posts/aspire-field-notes-portable-state-and-config/) does not override a deployment target's limitations.

The deployment identity, image-pull identity, and workload identities also have different jobs. Permission to pull an image from a registry does not grant the running application access to a database.

## Publishing is a review point, not proof of a deployment

The walkthrough stops the running catalog AppHost, then publishes with `Deployment__Target=compose`. In publish mode, the AppHost rejects a missing or unsupported target, so the target is never chosen implicitly. `aspire publish --list-steps` shows the pipeline before anything runs, and a real publish reports each step it executed:

{{< figure src="publish-summary.png" alt="Terminal output from aspire publish with Deployment__Target=compose: 8 of 8 steps succeeded, a step timeline from validate-compute-environments through publish-compose, and Pipeline succeeded" figureClass="full-width" >}}

Publishing executes registered pipeline steps and can build code or invoke tools. Review custom steps instead of treating it as a passive text renderer.[^publish] In this companion, publication does not build container images, run `docker compose up`, or deploy anything.

Open `artifacts/compose/docker-compose.yaml`, `.env`, and the generated `web.Dockerfile`. The companion's `review-compose.mjs` script parses Compose configuration without interpolation and asserts:

- `api`, `inventory`, `postgres`, and `web` are present.
- The API has database and inventory references.
- `DATA_PATH` is `/data`, and a named volume (`catalog-state` in the generated output) is mounted there.
- The frontend's `/api/{**catch-all}` route preserves the `/api` prefix.
- Only the frontend and optional dashboard expose host ports.
- The intentional fault is disabled, and the database password is represented by a secret placeholder.

The resulting `review.json` contains `deployed: false`, the reviewed Compose file's SHA-256, and no secret values. The review script deletes any earlier `review.json` before checking and writes a new one only when every assertion passes, so a stale passing result cannot sit beside newly generated files. It does not fill `.env` with credentials or resolve deployment-specific image placeholders.

Read the generated image references as well. With 13.6.1, `web.Dockerfile` builds the frontend on `node:22-slim` and serves it from `mcr.microsoft.com/dotnet/nightly/yarp:2.3-preview`, and the Compose dashboard uses `mcr.microsoft.com/dotnet/nightly/aspire-dashboard:13.6`. Nightly and preview images are a deliberate review item before any real deployment; pin or replace them according to your own image policy.

The frontend's publishing configuration explains why the browser route remains the same:

```csharp
#pragma warning disable ASPIREJAVASCRIPT001 // PublishAsStaticWebsite is still experimental in 13.6.
web.PublishAsStaticWebsite("/api", api, options => options.StripPrefix = false);
#pragma warning restore ASPIREJAVASCRIPT001
```

`PublishAsStaticWebsite` dates from 13.3 and is still experimental in 13.6. It generates a static-site and YARP publishing model. `StripPrefix` already defaults to `false`, so the generated route forwards `/api/catalog` unchanged; the companion sets it explicitly to document that contract. Setting it to `true` would remove the prefix, and the API would receive `/catalog` instead of its actual `/api/catalog` endpoint. Vite's development proxy is not the production server.

For the separate Sandboxes target, published Bicep describes infrastructure while sandboxes, disk images, ports, and URLs are created through its deployment workflow. That is another reason a static publish folder is not a completed deployment.

For other targets, inspect the generated routing, environment-variable names, mounts, secret references, and image configuration. A successful pipeline says its steps completed; it does not prove that an application-level request or access-control rule is correct.

## What 13.6 improves for an existing deployment

The new preview targets are only part of the release. Existing Kubernetes and Azure workflows also get useful corrections:[^release]

- Routes without an explicit hostname can inherit the configured hostname rather than losing it.
- Helm values retain parameters embedded in environment expressions.
- AKS environments can provision persistent-volume resources.
- Deployment state is scoped beneath `ASPIRE_HOME`, including separate identities for sibling single-file AppHosts.

These changes make it easier to express the intended deployment. They are still reasons to compare the generated output before and after an upgrade, especially if a previous workaround compensated for an older behavior.

## Upgrade the behavior, not just the version number

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

Add cold-start, scale, or concurrency checks when they are part of the workload's requirements. Do not publish invented performance numbers to fill a results table; collect them for the environment you actually deploy.

## The loop is the point

We started by keeping a failure instead of losing it during a restart. We modeled the application, brought diagnostic tools to its resources, gave agents an evidence-based workflow, and made state and configuration explicit.

Deployment should preserve that habit. Choose the target for the promises it can keep, and verify those promises with an application result.

Return to the [series reading path](/series/aspire-field-notes/) when the next problem is local rather than deployed. The tool changes; the need for a clear observation and a repeatable check does not.

[^express]: [Container Apps Express behavior, limitations, and experimental diagnostic](https://aspire.dev/deployment/azure/container-apps/#express-environments).

[^sandboxes]: [Sandboxes prerequisites, identities, publishing, deployment, and limitations](https://aspire.dev/deployment/azure/sandboxes/).

[^publish]: [`aspire publish` pipeline and command options](https://aspire.dev/reference/cli/commands/aspire-publish/).

[^release]: [Aspire 13.6 deployment changes and migration guidance](https://aspire.dev/whats-new/aspire-13-6/).

[^models]: [GitHub Models retirement](https://github.blog/changelog/2026-07-30-github-models-is-now-retired/) and [Aspire migration guidance](https://aspire.dev/integrations/ai/github-models/github-models-get-started/).
