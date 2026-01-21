---
title: Aspire CLI Part 2 - Deployment and Pipelines
draft: true
categories:
- Development
tags:
- Aspire
- CLI
- Azure
- Deployment
- CI/CD
- distributed-systems
image: images/logos/dotnet-aspire-logo.png
featureImage: images/logos/dotnet-aspire-logo.png
slug: aspire-cli-part-2
---

In [Part 1](/posts/aspire-cli-getting-started/), we covered the basics of the Aspire CLI: creating projects with `aspire new`, adding Aspire to existing apps with `aspire init`, running with `aspire run`, and managing integrations with `aspire add`. Now let's dive into deployment and CI/CD pipelines.

<!--more-->

## Deployment with Aspire

Once your distributed application is running locally, the next step is getting it deployed. Aspire provides two key commands for this: `aspire publish` and `aspire deploy`.

### `aspire publish` - Generate Deployment Artifacts

The `aspire publish` command generates deployment manifests and artifacts for your target platform.

```bash
# Generate deployment artifacts
aspire publish
```

**Supported targets:**

| Target | Description |
| ------ | ----------- |
| Azure Container Apps | Serverless containers on Azure |
| Kubernetes | K8s manifests for any cluster |
| Docker Compose | For self-hosted deployments |

### `aspire deploy` - Deploy to Cloud

The `aspire deploy` command handles the full deployment workflow.

```bash
# Deploy to Azure Container Apps
aspire deploy --target aca

# Deploy to Kubernetes
aspire deploy --target k8s
```

## CI/CD with `aspire do`

The `aspire do` command enables pipeline automation without complex scripts.

```bash
# Run in CI/CD pipeline
aspire do build
aspire do test
aspire do publish
```

## Azure Container Apps Deployment

Here's a complete example deploying to Azure Container Apps:

```bash
# Prerequisites
az login
az account set --subscription "Your-Subscription"

# Deploy
aspire deploy --target aca --resource-group my-rg --environment my-env
```

## Kubernetes Deployment

For Kubernetes deployments:

```bash
# Generate K8s manifests
aspire publish --target k8s --output ./k8s

# Apply to cluster
kubectl apply -f ./k8s
```

## GitHub Actions Integration

Example workflow for CI/CD:

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
          dotnet-version: '9.0.x'
      
      - name: Install Aspire CLI
        run: curl -fsSL https://aspire.dev/install.sh | bash
      
      - name: Build and Test
        run: |
          aspire do build
          aspire do test
      
      - name: Deploy to Azure
        run: aspire deploy --target aca
        env:
          AZURE_CREDENTIALS: ${{ secrets.AZURE_CREDENTIALS }}
```

## Learn More

- [Aspire Deployment Docs](https://aspire.dev/deployment/)
- [Azure Container Apps Integration](https://aspire.dev/integrations/azure-container-apps/)
- [Kubernetes Deployment Guide](https://aspire.dev/deployment/kubernetes/)

## Wrapping Up

With `aspire publish`, `aspire deploy`, and `aspire do`, you have everything needed to take your Aspire application from local development to production deployment.

Stay tuned for Part 3 where we'll cover advanced scenarios like multi-environment configurations and custom integrations.

Until next time, happy Aspiring!

