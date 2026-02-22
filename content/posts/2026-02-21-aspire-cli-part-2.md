---
title: "Aspire CLI Part 2 - Deployment and Pipelines"
date: '2026-02-21'
categories:
- Development
tags:
- Aspire
- CLI
- Azure
- dotnet
- distributed-systems
- Deployment
- CI/CD
image: images/dotnet-aspire-logo.png
featureImage: images/dotnet-aspire-logo.png
slug: aspire-cli-part-2
aliases:
- /2026/02/21/aspire-cli-part-2/
---

In [Part 1](/posts/aspire-cli-getting-started/), we covered the basics of the Aspire CLI: creating projects with `aspire new`, adding Aspire to existing apps with `aspire init`, running with `aspire run`, and managing integrations with `aspire add` and `aspire update`. Now let's dive into deployment and CI/CD pipelines.

<!--more-->

> **Prerequisite:** Aspire 13 requires .NET SDK 10.0.100 or later. Make sure you have it installed before using the commands in this post.

## The Publish and Deploy Model

Aspire separates deployment into two distinct phases:

1. **Publish** (`aspire publish`) — Generates intermediate, parameterized deployment artifacts (Compose files, Kubernetes manifests, Bicep templates, etc.)
2. **Deploy** (`aspire deploy`) — Resolves parameters and applies those artifacts to a target environment

This separation is intentional. Published assets contain **placeholders** instead of concrete values — secrets and environment-specific configuration are injected later at deploy time. This keeps sensitive data out of your artifacts and enables the same published output to target multiple environments.

## `aspire publish` - Generate Deployment Artifacts

The `aspire publish` command generates deployment artifacts based on the **compute environments** configured in your AppHost. A compute environment represents a target platform and determines what gets generated.

```bash
aspire publish -o ./artifacts
```

The output depends on which hosting integration packages you've added:

| NuGet Package | Target | Publish | Deploy |
|---|---|---|---|
| `Aspire.Hosting.Docker` | Docker Compose | ✅ Yes | 🧪 Preview |
| `Aspire.Hosting.Kubernetes` | Kubernetes | ✅ Yes | 🧪 Preview |
| `Aspire.Hosting.Azure.AppContainers` | Azure Container Apps | ✅ Yes | ✅ Yes (Preview) |
| `Aspire.Hosting.Azure.AppService` | Azure App Service | ✅ Yes | ✅ Yes (Preview) |

If no integration supports publishing, `aspire publish` will tell you:

```text
No resources in the distributed application model support publishing.
```

### Parameterized Output

Published artifacts contain placeholders rather than concrete values. For example, a Docker Compose publish might generate:

```yaml
services:
  pg:
    image: "docker.io/library/postgres:17.2"
    environment:
      POSTGRES_PASSWORD: "${PG_PASSWORD}"
    ports:
      - "8000:5432"
  api:
    image: "${API_IMAGE}"
    environment:
      ConnectionStrings__db: "Host=pg;Port=5432;Username=postgres;Password=${PG_PASSWORD};Database=db"
```

Notice `${PG_PASSWORD}` and `${API_IMAGE}` are **not resolved** during publish. You supply their values at deploy time — through environment variables, `.env` files, or CI/CD pipeline secrets.

### Docker Compose Example

The most common pattern from the [Aspire samples](https://github.com/davidfowl/aspire-13-samples) uses Docker Compose as the compute environment. See the [Docker Compose sample](https://github.com/codebytes/blog-samples/tree/main/aspire-cli/aspire-docker-compose) for a complete working example.

```csharp
#:package Aspire.Hosting.Docker@13-*
#:sdk Aspire.AppHost.Sdk@13.0.0

var builder = DistributedApplication.CreateBuilder(args);

builder.AddDockerComposeEnvironment("dc");

var postgres = builder.AddPostgres("postgres")
                      .WithDataVolume()
                      .WithPgAdmin();
var db = postgres.AddDatabase("db");

builder.AddCSharpApp("api", "./api")
       .WithHttpHealthCheck("/health")
       .WithExternalHttpEndpoints()
       .WaitFor(db)
       .WithReference(db);

builder.Build().Run();
```

Then the standard workflow is:

```bash
aspire run                          # Run locally
aspire publish -o ./artifacts       # Generate Docker Compose files
aspire deploy                       # Deploy to Docker Compose
aspire do docker-compose-down-dc    # Tear down the deployment
```

### Azure Container Apps Example

For Azure, add the Azure Container Apps environment. See the [Azure Container Apps sample](https://github.com/codebytes/blog-samples/tree/main/aspire-cli/aspire-container-apps) for a complete working example.

```csharp
#:package Aspire.Hosting.Azure.AppContainers@13.0.0
#:package Aspire.Hosting.Azure.Storage@13.0.0
#:sdk Aspire.AppHost.Sdk@13.0.0

var builder = DistributedApplication.CreateBuilder(args);

builder.AddAzureContainerAppEnvironment("env");

var storage = builder.AddAzureStorage("storage")
                     .RunAsEmulator();

var blobs = storage.AddBlobContainer("images");

builder.AddProject<Projects.Api>("api")
       .WithExternalHttpEndpoints()
       .WithReference(blobs);

builder.Build().Run();
```

Publishing this generates **Bicep templates** that you can review, customize, and deploy:

```bash
aspire publish -o ./azure-artifacts   # Generates Bicep files
aspire deploy                         # Deploys to Azure Container Apps
```

### Kubernetes Example

For Kubernetes, add the hosting package and configure a compute environment. See the [Kubernetes sample](https://github.com/codebytes/blog-samples/tree/main/aspire-cli/aspire-kubernetes) for a complete working example.

```csharp
var builder = DistributedApplication.CreateBuilder(args);

var k8s = builder.AddKubernetesEnvironment("k8s");

var api = builder.AddProject<Projects.Api>("api")
    .WithExternalHttpEndpoints();

builder.Build().Run();
```

Generate and deploy:

```bash
# Generate Kubernetes manifests
aspire publish -o ./k8s-output

# Apply with kubectl or Helm
kubectl apply -f ./k8s-output
```

### Multiple Compute Environments

If you add multiple compute environments, Aspire needs to know which resource goes where. Use `WithComputeEnvironment` to disambiguate:

```csharp
var k8s = builder.AddKubernetesEnvironment("k8s-env");
var compose = builder.AddDockerComposeEnvironment("docker-env");

builder.AddProject<Projects.Frontend>("frontend")
    .WithComputeEnvironment(k8s);

builder.AddProject<Projects.Backend>("backend")
    .WithComputeEnvironment(compose);
```

Without this, Aspire throws an ambiguous environment exception at publish time.

## `aspire deploy` - Deploy to a Target

The `aspire deploy` command resolves parameters and applies published artifacts to a target environment. This command is in **preview** and under active development.

```bash
aspire deploy
```

> **Note:** The deploy command may change as it matures. Keep an eye on the [.NET Blog](https://devblogs.microsoft.com/dotnet) and the [Aspire deployment docs](https://aspire.dev/deployment/overview/) for updates.

What happens depends on your compute environment:

- **Docker Compose** — Builds images, resolves variables, runs `docker compose up`
- **Azure Container Apps** — Provisions Azure resources, builds and pushes container images, deploys apps
- **Kubernetes** — Generates manifests and applies them

For Docker Compose deployments, the workflow from the official samples is straightforward:

```bash
aspire run      # Run locally
aspire deploy   # Deploy to Docker Compose
aspire do docker-compose-down-dc  # Teardown
```

For Azure deployments, `aspire deploy` prompts for:

1. **Azure sign-in** and subscription selection
2. **Resource group** creation or selection
3. **Location** for Azure resources

The command then provisions infrastructure, builds containers, pushes to ACR, and deploys — all in one step.

For non-interactive deployment (CI/CD), set these environment variables to skip the prompts:

```bash
Azure__SubscriptionId=<your-subscription-id>
Azure__Location=<azure-region>
Azure__ResourceGroup=<resource-group-name>
```

## `aspire do` - Pipeline Automation

The `aspire do` command executes pipeline steps defined by hosting integrations. Use `aspire do diagnostics` to discover what steps are available and their dependencies:

```bash
# List available pipeline steps
aspire do diagnostics

# Tear down a Docker Compose deployment
aspire do docker-compose-down-dc

# The naming convention is: docker-compose-down-{environment-name}
```

Well-known pipeline steps include `build`, `push`, `publish`, and `deploy`. Resources can contribute custom steps — for example, Docker Compose adds teardown steps. This command is particularly useful in CI/CD pipelines and for managing environment lifecycle.

## `aspire exec` - Run Commands in Resource Context

The `aspire exec` command runs commands in the context of a specific resource with the correct connection strings and environment variables. This command is disabled by default — enable it first. See the [exec sample](https://github.com/codebytes/blog-samples/tree/main/aspire-cli/aspire-exec) for a complete working example with Postgres and Redis.

```bash
# Enable the exec feature
aspire config set features.execCommandEnabled true
```

Then use the `--resource` (or `-r`) flag to specify the target:

```bash
# Run EF Core migrations
aspire exec --resource mydb -- dotnet ef database update

# Open an interactive shell in a container
aspire exec --resource redis -- redis-cli

# Start a dependency and then run against it
aspire exec --start-resource mydb -- dotnet ef migrations add Init
```

The `--start-resource` (or `-s`) flag is useful when you need to start a resource (and its dependencies) before running a command against it.

## Azure Developer CLI (azd) Integration

For production Azure deployments, the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/) (`azd`) has first-class Aspire support and is the more mature deployment path:

```bash
# Initialize azd in your project directory
azd init

# Provision infrastructure and deploy in one command
azd up
```

During `azd init`, you'll:

1. Select which services to expose to the internet
2. Name your environment (e.g., `dev`, `prod`)
3. Choose your Azure subscription and location

The `azd up` command handles the full lifecycle: `azd package` → `azd provision` → `azd deploy`. Projects are packaged into containers, Azure resources are provisioned via Bicep, and containers are pushed to Azure Container Registry and deployed to Container Apps.

Generated files:

- `azure.yaml` — Maps Aspire AppHost services to Azure resources
- `.azure/config.json` — Active environment configuration
- `.azure/{env}/.env` — Environment-specific overrides
- `.azure/{env}/config.json` — Public endpoint configuration

## GitHub Actions

### Using azd (Recommended for Azure)

```yaml
name: Deploy Aspire App

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'

      - name: Install azd
        uses: Azure/setup-azd@v2

      - name: Log in to Azure
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Provision and Deploy
        run: azd up --no-prompt
        env:
          AZURE_ENV_NAME: ${{ vars.AZURE_ENV_NAME }}
          AZURE_LOCATION: ${{ vars.AZURE_LOCATION }}
          AZURE_SUBSCRIPTION_ID: ${{ vars.AZURE_SUBSCRIPTION_ID }}
```

### Using Aspire CLI

```yaml
name: Deploy with Aspire CLI

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'

      - name: Install Aspire CLI
        run: curl -fsSL https://aspire.dev/install.sh | bash

      - name: Publish artifacts
        run: aspire publish -o ./artifacts
        working-directory: ./src/MyApp.AppHost

      - name: Deploy with Docker Compose
        run: |
          cd ./artifacts
          docker compose up --build -d
```

## Legacy Manifest Format

Starting with Aspire 9.2, the single deployment manifest is being phased out in favor of the `aspire publish` / `aspire deploy` model with hosting integration extensibility. The legacy manifest is still available for debugging:

```bash
aspire do publish-manifest --output-path ./diagnostics
```

This produces a manifest snapshot for inspecting resource graphs and troubleshooting, but it's not the primary deployment path.

## Learn More

- [Publishing and Deployment Overview](https://aspire.dev/deployment/overview/)
- [Aspire CLI Reference](https://aspire.dev/reference/cli/overview/)
- [Deploy to Azure Container Apps](https://aspire.dev/deployment/azure/aca-deployment-aspire-cli/)
- [Azure Developer CLI with Aspire](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Aspire Samples (davidfowl)](https://github.com/davidfowl/aspire-13-samples)
- [Official Aspire Samples](https://github.com/dotnet/aspire-samples)
- [Blog Post Samples](https://github.com/codebytes/blog-samples/tree/main/aspire-cli)

## Wrapping Up

The publish/deploy model gives you flexibility: publish generates parameterized artifacts, and deploy resolves values and applies them. Whether you're targeting Docker Compose for local staging, Kubernetes for container orchestration, or Azure Container Apps for managed hosting, the workflow is consistent.

For production Azure deployments, I recommend `azd` for its mature infrastructure-as-code capabilities. For Docker Compose and local deployment workflows, `aspire deploy` is increasingly capable as it matures.

In [Part 3](/posts/aspire-cli-part-3-mcp/), we explore one of Aspire's most exciting features: MCP (Model Context Protocol) integration, which lets AI coding agents like GitHub Copilot and Claude understand and interact with your running Aspire applications.

Until next time, happy Aspiring!

## Related Posts

- [Getting Started with the Aspire CLI](/posts/aspire-cli-getting-started/)
- [Aspire CLI Part 3 - MCP for AI Coding Agents](/posts/aspire-cli-part-3-mcp/)
