---
title: "Aspire CLI Part 3 - MCP for AI Coding Agents"
draft: true
categories:
- Development
tags:
- dotnet
- Aspire
- AI
- MCP
- GitHub-Copilot
- Claude
- distributed-systems
image: images/dotnet-aspire-logo.png
featureImage: images/dotnet-aspire-logo.png
slug: aspire-cli-part-3-mcp
---

In [Part 1](/posts/aspire-cli-getting-started/), we covered creating and running Aspire apps. In [Part 2](/posts/aspire-cli-part-2/), we explored deployment and CI/CD. Now let's look at one of Aspire's most exciting features: MCP (Model Context Protocol) support for AI coding agents.

<!--more-->

Aspire MCP enables AI coding agents to understand and interact with your distributed applications. Your AI assistant can query resource states, debug with real-time logs, and investigate telemetry across your entire system — without you having to copy/paste anything.

## What is Aspire MCP?

The Aspire MCP server is a local [Model Context Protocol](https://modelcontextprotocol.io/) server built into the Aspire dashboard. Starting with Aspire 9.0, MCP support has been available (manual configuration), and Aspire 13.1 added the `aspire mcp init` command for automatic setup.

It bridges the gap between your running distributed application and AI coding assistants like GitHub Copilot, Claude Code, Cursor, and OpenAI Codex.

With Aspire MCP, your AI assistant can:

- **Query resources** — Get resource states, endpoints, health status, and available commands
- **Debug with logs** — Access real-time console logs from any resource
- **Investigate telemetry** — Analyze structured logs and distributed traces across services
- **Execute commands** — Run resource commands directly
- **Discover integrations** — Find and understand available Aspire hosting integrations

This transforms your AI assistant from a code generator into a development partner that understands your running system.

## Getting Started

There are two ways to configure MCP: automatically with the CLI (13.1+) or manually through the dashboard (9.0+).

### Option 1: Using the Aspire CLI (Recommended)

Starting with Aspire 13.1, the `aspire mcp init` command detects and configures your AI assistant automatically:

```bash
cd your-aspire-project
aspire mcp init
```

The command walks you through an interactive selection:

```text
Which agent environments do you want to configure?
[ ] Configure VS Code to use the Aspire MCP server
[ ] Configure GitHub Copilot CLI to use Aspire MCP server
[ ] Configure Claude Code to use Aspire MCP server
[ ] Configure Open Code to use Aspire MCP server

Which additional options do you want to enable?
[ ] Create an agent instructions file (AGENTS.md)
[ ] Configure Playwright MCP server
```

Select your preferred AI assistants and the CLI generates the appropriate configuration files (`.vscode/mcp.json`, `.claude/`, etc.).

### Option 2: Manual Configuration

For Aspire 9.0 through 13.0, or when you want more control:

1. Run your Aspire app with `aspire run`
2. Open the Aspire dashboard
3. Click the **MCP** button in the top right corner
4. Use the displayed settings to configure your AI assistant

The key settings you'll need:

| Setting | Description |
|---------|-------------|
| `url` | Aspire MCP address |
| `type` | `http` (streamable-HTTP MCP server) |
| `x-mcp-api-key` | HTTP header for securing access |

Configuration varies by AI assistant. Consult your tool's MCP documentation to add these settings.

## MCP Tools Available

Once connected, your AI assistant gains access to several powerful tools:

### Resource Management

- **`list_resources`** - Lists all resources with state, health status, endpoints, and commands
- **`execute_resource_command`** - Executes commands on specific resources

### Logging and Telemetry

- **`list_console_logs`** - Gets console logs for a resource
- **`list_structured_logs`** - Retrieves structured logs, optionally filtered by resource
- **`list_traces`** - Lists distributed traces across your system
- **`list_trace_structured_logs`** - Gets structured logs for a specific trace

### Integration Discovery

- **`list_integrations`** - Shows available Aspire hosting integrations with package IDs and versions
- **`get_integration_docs`** - Retrieves documentation for a specific integration package

### AppHost Management

- **`list_apphosts`** - Lists all AppHosts in the workspace
- **`select_apphost`** - Switches context to a specific AppHost

## Example Prompts

After configuring MCP, try these prompts with your AI assistant:

- *"Are all my resources running?"*
- *"Show me the last 50 log entries from the API service"*
- *"Analyze HTTP request performance for the webfrontend"*
- *"What traces show errors in the last 5 minutes?"*
- *"Restart unhealthy resources"*
- *"What Aspire integrations are available for Redis?"*

## Excluding Resources from MCP

You may have resources with sensitive data that shouldn't be exposed to AI assistants. Annotate them in your AppHost:

```csharp
var builder = DistributedApplication.CreateBuilder(args);

var apiservice = builder.AddProject<Projects.Api>("api")
    .ExcludeFromMcp();  // This resource hidden from MCP

builder.AddProject<Projects.Web>("web")
    .WithReference(apiservice);

builder.Build().Run();
```

This excludes the resource **and its associated telemetry** from all MCP results.

## A Practical Example

Consider a polyglot application using the Aspire CLI with AI-assisted development. Here's a sample AppHost from the [Aspire 13 samples](https://github.com/davidfowl/aspire-13-samples):

```csharp
#:package Aspire.Hosting.OpenAI@13.0.0
#:package Aspire.Hosting.Python@13.0.0
#:package Aspire.Hosting.Docker@13-*
#:sdk Aspire.AppHost.Sdk@13.0.0

var builder = DistributedApplication.CreateBuilder(args);

builder.AddDockerComposeEnvironment("dc");

var openai = builder.AddOpenAI("openai");

builder.AddUvicornApp("ai-agent", "./agent", "main:app")
    .WithUv()
    .WithExternalHttpEndpoints()
    .WithEnvironment("OPENAI_API_KEY", openai.Resource.Key);

builder.Build().Run();
```

After running `aspire mcp init` and `aspire run`, you can ask your AI assistant things like:

- *"Is the ai-agent resource healthy?"*
- *"Show me any errors in the agent logs"*
- *"What OpenTelemetry traces have the longest duration?"*

The AI sees the Python service, the OpenAI connection, health check status, logs, and traces — all in real time. No more copying log output into chat windows.

## Supported AI Assistants

Configuration varies by assistant. Here are the supported tools and their documentation:

| Assistant | Configuration Docs |
|-----------|-------------------|
| Claude Code | [MCP configuration](https://docs.claude.com/en/docs/claude-code/mcp) |
| GitHub Copilot CLI | [Add MCP server](https://docs.github.com/copilot/how-tos/use-copilot-agents/use-copilot-cli#add-an-mcp-server) |
| VS Code Copilot | [MCP servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) |
| Visual Studio | [MCP configuration](https://learn.microsoft.com/visualstudio/ide/mcp-servers) |
| Cursor | [Installing MCP servers](https://cursor.com/docs/context/mcp#installing-mcp-servers) |
| OpenAI Codex | [MCP setup](https://developers.openai.com/codex/mcp/) |

## Securing the API Key

The `x-mcp-api-key` secures access to MCP, but your AI assistant needs access to it. Use your tool's secure storage features:

**VS Code Example** - Use [input variables](https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_input-variables-for-sensitive-data) to avoid committing the key to source control in `mcp.json`.

## Troubleshooting

### Self-Signed Certificate Issues

Some AI assistants don't support self-signed HTTPS certificates. If you encounter connection issues:

1. If you use the `http` launch profile, you're already set
2. For HTTPS, configure just the MCP endpoint to use HTTP in `launchSettings.json`:

```json
{
  "profiles": {
    "https": {
      "environmentVariables": {
        "ASPIRE_DASHBOARD_MCP_ENDPOINT_URL": "http://localhost:16036",
        "ASPIRE_ALLOW_UNSECURED_TRANSPORT": "true"
      }
    }
  }
}
```

> **Caution**: This removes transport security from MCP communication.

### Data Size Limits

AI models have context limits. Aspire MCP automatically:

- Truncates large data fields (like exception stack traces)
- Omits older items from large telemetry collections

## Why This Matters

Traditional AI coding assistants work with static code. Aspire MCP connects them to your **running system**. This enables scenarios like:

- **"Why is the checkout service slow?"** - The AI can analyze traces and identify the bottleneck
- **"Debug this 500 error"** - The AI accesses structured logs to find the root cause
- **"Is my database connection healthy?"** - The AI checks resource health status directly

Instead of asking you to describe your system, the AI can observe it directly.

## Learn More

- [Aspire MCP Server Documentation](https://aspire.dev/dashboard/mcp-server/)
- [Configure MCP Quick Start](https://aspire.dev/get-started/configure-mcp/)
- [aspire mcp init Command Reference](https://aspire.dev/reference/cli/commands/aspire-mcp-init/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)

## Related Posts

- [Getting Started with the Aspire CLI](/posts/aspire-cli-getting-started/)
- [Aspire CLI Part 2 - Deployment and Pipelines](/posts/aspire-cli-part-2/)

## Wrapping Up

Aspire MCP represents a shift in how we interact with distributed applications during development. By giving AI assistants real-time access to your running system, you unlock debugging and development workflows that weren't possible before.

Try `aspire mcp init` in your next project and see how it transforms your AI-assisted development experience.

Until next time, happy Aspiring!
