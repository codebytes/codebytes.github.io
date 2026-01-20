---
title: Getting Started with the Aspire CLI - A Complete Guide
date: '2025-12-11'
categories:
- Development
tags:
- Aspire
- CLI
- tooling
- distributed-systems
- orchestration
image: images/dotnet-aspire-logo.png
featureImage: images/dotnet-aspire-logo.png
aliases:
- /2025/12/11/aspire-cli-getting-started/
- /dotnet/aspire-cli-getting-started/
slug: aspire-cli-getting-started
---
**This blog was posted as part of the [C# Advent Calendar 2025](https://csadvent.christmas/). Make sure to check out everyone else's work when you're done here**

The Aspire CLI is a cross-platform tool for creating, managing, and running polyglot Aspire projects. This post covers the core commands you'll use day-to-day.

<!--more-->

## What is Aspire?

**Aspire** is an opinionated, cloud-ready stack for building observable distributed applications. Think: a C# AppHost that models your topology, plus integrations and tooling.

### Polyglot by Design

While Aspire started in the **.NET** ecosystem, **Aspire 13.0 made Python and JavaScript first-class citizens**.

- **.NET projects** - ASP.NET Core APIs, Blazor apps, Worker Services, Azure Functions
- **Python applications** - Flask, FastAPI, Django, or any Python script
- **JavaScript/Node.js apps** - Express, Next.js, or any Node.js application
- **Containers** - Any Docker image you need

The AppHost (orchestrator) is written in C#, but it can coordinate services written in any language.

That said, **.NET remains the sweet spot** for Aspire because you get the richest integration and tooling.

---

### The Problem Aspire Solves

Coordinating multiple services usually means lots of config, hard-coded URLs, and fragile startup order. Aspire helps by giving you:

- **Orchestration** - Model resources and dependencies in code
- **Integrations** - Standard components for common infrastructure
- **Tooling** - A dashboard + CLI to run and debug the system

### Dashboards and Telemetry

Aspire includes a local **dashboard** that helps you understand what’s running: resource status, endpoints, logs, traces, and metrics.

Telemetry is typically emitted via **OpenTelemetry** (the ServiceDefaults project wires a lot of this up for .NET services). By default this is a local developer experience. Data only goes to an external backend if you configure an exporter to send it there.

### The AppHost: Your Application's Control Plane

At the heart of every Aspire application is the **AppHost**. It defines resources and dependencies (and can include health checks and external endpoints).

```csharp
var builder = DistributedApplication.CreateBuilder(args);

// TODO: Add resources here

builder.Build().Run();
```

### ServiceDefaults: Shared Configuration

The **ServiceDefaults** project is a shared library for observability and resilience (health checks, OpenTelemetry, logging, etc.).

Each service references ServiceDefaults and calls two methods:

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.AddServiceDefaults();

var app = builder.Build();
app.MapDefaultEndpoints();
app.Run();
```

This ensures consistent observability across all services without duplicating configuration.

## Aspire vs Docker Compose

If you're currently using Docker Compose, here's the mental model shift.

**Docker Compose:**

```yaml
services:
  postgres:
    image: postgres:latest

  api:
    build: ./api
    depends_on:
      - postgres

  web:
    build: ./web
    depends_on:
      - api
```

**Aspire equivalent:**

```csharp
var builder = DistributedApplication.CreateBuilder(args);

var postgres = builder.AddPostgres("postgres")
    .AddDatabase("mydb");

var api = builder.AddProject<Projects.Api>("api")
    .WithReference(postgres);

var web = builder.AddProject<Projects.Web>("web")
    .WithReference(api)
    .WaitFor(api);

builder.Build().Run();
```

**Why Aspire often feels better:**

- **Less config glue** - Model topology in code
- **Service discovery by default** - Fewer hard-coded URLs
- **Built-in dashboard** - Logs, traces, and metrics in one place
- **Integrations** - Common infra with sensible defaults
- **Polyglot** - C#, Python, JavaScript, containers

## Why the Aspire CLI?

The Aspire CLI helps you scaffold, run, and evolve an Aspire application without a pile of scripts and config.

**What you’ll use it for:**

- Create or Aspireify a solution
- Run the apphost and open the dashboard
- Add integrations and keep packages current

Key takeaways:
- **`aspire new`** for greenfield projects with full scaffolding
- **`aspire init`** to add Aspire to existing solutions incrementally
- **`aspire run`** for development with the built-in dashboard
- **`aspire add`** to easily integrate databases, caches, and queues
- **`aspire update`** to keep packages current

## Prerequisites

Before installing the Aspire CLI, ensure you have the following:

| Requirement | Details |
|-------------|---------|
| .NET 8+ SDK | Required for Aspire 13.0+. Run `dotnet --info` to verify. The CLI needs the SDK even if your apps target .NET 8 or 9. |
| Editor/IDE | VS Code with C# Dev Kit and Aspire extensions, Visual Studio 2022 17.13+, or JetBrains Rider. |
| Optional | GitHub Codespaces or Dev Containers for cloud-based development. |

## Installing the Aspire CLI

The install scripts download the CLI and add it to your PATH.

| Platform | Install command |
| --- | --- |
| Windows (PowerShell) | `irm https://aspire.dev/install.ps1 \| iex` |
| macOS and Linux (bash) | `curl -fsSL https://aspire.dev/install.sh \| bash` |

If `aspire` isn't found, open a new terminal and try again.

## Core CLI Commands

The Aspire CLI provides several commands for different stages of the development lifecycle. Here's a practical rundown of the core commands.

### `aspire new` - Create a New Solution

Use `aspire new` for greenfield projects.

**Basic usage:**

```bash
# Interactive mode - prompts for template, name, and output
aspire new

# Non-interactive with explicit options
aspire new aspire-starter -n AspireApp -o AspireApp
```

**What gets created:**

```text
AspireApp/
├── AspireApp.sln
├── AspireApp.AppHost/           # Dev-time orchestrator
│   ├── AppHost.cs
│   └── AspireApp.AppHost.csproj
├── AspireApp.ServiceDefaults/   # Shared configuration
│   ├── Extensions.cs
│   └── AspireApp.ServiceDefaults.csproj
├── AspireApp.ApiService/        # Mock weather data API
│   ├── Program.cs
│   └── AspireApp.ApiService.csproj
└── AspireApp.Web/               # Blazor frontend
    ├── Program.cs
    └── AspireApp.Web.csproj
```

You get an AppHost, ServiceDefaults, and a small starter app you can run immediately.

---

### `aspire init` - Add Aspire to Existing Apps

Already have a codebase? `aspire init` adds an AppHost so you can orchestrate what you already have (including Python and JavaScript).

```bash
# Navigate to your solution directory
cd /path/to/your-solution

# Initialize Aspire support
aspire init
```

The command runs in interactive mode and will create `apphost.cs` plus minimal run configuration.

**After running `aspire init`:**

Your project root gets a file-based AppHost:

```text
my-saas-app/
  apphost.cs          # (new) orchestration code
  apphost.run.json    # (new) local run configuration
  api/
    main.py
    pyproject.toml
  frontend/
    app.py
    requirements.txt
  worker/
    worker.py
    requirements.txt
```

The initial `apphost.cs` is minimal:

```csharp
#:sdk Aspire.AppHost.Sdk@13.0.0

var builder = DistributedApplication.CreateBuilder(args);

// TODO: Add resources here

builder.Build().Run();
```

**Example: reference a Python API from a Python worker**

If you’re orchestrating Python services, add the Python hosting integration to your AppHost:

```bash
aspire add python
```

Then wire resources in the AppHost using `AddUvicornApp` (for FastAPI, Flask, and other ASGI apps) and `AddPythonApp` for a worker. `WithReference(...)` declares the dependency and Aspire injects the connection info as environment variables.

```csharp
var builder = DistributedApplication.CreateBuilder(args);

var api = builder.AddUvicornApp("api", "./api", "main:app")
  .WithUv()
  .WithHttpHealthCheck("/health");

var worker = builder.AddPythonApp("worker", "./worker", "worker.py")
  .WithUv()
  .WithReference(api); // Worker gets API_HTTP and API_HTTPS env vars

builder.Build().Run();
```

### `aspire new` vs `aspire init`

| Scenario | Command | Why |
|----------|---------|-----|
| Starting fresh with a new project | `aspire new` | Scaffolds everything: solution, AppHost, ServiceDefaults, sample projects |
| Adding Aspire to existing code | `aspire init` | Preserves your existing projects, adds only orchestration layer |
| Polyglot app (C#, Python, JS) | `aspire init` | Works with existing multi-language repos |
| Learning Aspire | `aspire new` | Get a working example immediately |

---

### `aspire run` - Run the Distributed App

`aspire run` builds and starts your resources and opens the dashboard.

```bash
# From your solution directory
aspire run
```

**What happens:**

1. Finds the AppHost
2. Builds and starts resources
3. Prints the dashboard URL

**Example output:**

```text
Dashboard:  https://localhost:17068/login?t=ea559845d54cea66b837dc0ff33c3bd3
Logs:       ~/.aspire/cli/logs/apphost-13024-2025-10-31-19-40-58.log
```

**A note on the dashboard and telemetry**

The dashboard is where you’ll see status, logs, traces, and metrics for the running app.

---

### `aspire add` - Add Integrations

`aspire add` adds official integration packages to your AppHost.

```bash
# Interactive mode - shows list of available integrations
aspire add

# Add a specific integration by name
aspire add redis
```

After adding an integration, wire it in your AppHost:

```csharp
var builder = DistributedApplication.CreateBuilder(args);

// Add Redis resource
var cache = builder.AddRedis("cache");

// Share Redis with your API
var api = builder.AddProject<Projects.YourApi>("api")
    .WithReference(cache)
    .WithHttpHealthCheck("/health");

builder.Build().Run();
```

Then add the client library to your consuming project:

```bash
dotnet add YourApi package Aspire.StackExchange.Redis
```

Then configure the client in your service (for example, `builder.AddRedisClient("cache")`).

---

### `aspire update` - Update Packages and Templates

The `aspire update` command keeps your Aspire projects current by detecting and updating outdated packages and templates.

```bash
aspire update
```

If you want to update the **CLI itself** (instead of just your solution packages), use:

```bash
aspire update --self
```

## Practical Workflow

Here's a typical workflow for a new project:

```bash
# 1. Create a new solution
aspire new

# 2. Run it
aspire run

# 3. Add an integration
aspire add redis

# 4. Update packages (and optionally the CLI)
aspire update
aspire update --self
```

## Learn More

- [Install CLI](https://aspire.dev/get-started/install-cli/)
- [CLI Reference](https://aspire.dev/reference/cli/overview/)
- [Add Aspire to Existing App](https://aspire.dev/get-started/add-aspire-existing-app/)
- [Aspire Dashboard Overview](https://aspire.dev/dashboard/overview/)
- [Integrations Gallery](https://aspire.dev/integrations/gallery/)

## Wrapping Up

There is too much to cover here, so there will be follow-up posts on deployment (`aspire publish` / `aspire deploy`) and pipelines with `aspire do`.

Until next time, happy Aspiring!
