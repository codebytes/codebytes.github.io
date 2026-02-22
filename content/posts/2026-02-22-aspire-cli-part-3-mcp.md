---
title: "Aspire CLI Part 3 - MCP for AI Coding Agents"
date: '2026-02-22'
categories:
- Development
tags:
- Aspire
- CLI
- dotnet
- AI
- MCP
- distributed-systems
- GitHub-Copilot
image: images/dotnet-aspire-logo.png
featureImage: images/dotnet-aspire-logo.png
slug: aspire-cli-part-3-mcp
aliases:
- /2026/02/22/aspire-cli-part-3-mcp/
---

In [Part 1](/posts/aspire-cli-getting-started/), we covered creating and running Aspire apps. In [Part 2](/posts/aspire-cli-part-2/), we explored deployment and CI/CD. Now let's look at one of Aspire's most exciting features: MCP (Model Context Protocol) support for AI coding agents.

<!--more-->

Aspire MCP enables AI coding agents to understand and interact with your distributed applications. Your AI assistant can query resource states, debug with real-time logs, and investigate telemetry across your entire system — without you having to copy/paste anything.

## What is Aspire MCP?

The Aspire MCP server is a local [Model Context Protocol](https://modelcontextprotocol.io/) server that connects your AI coding assistants to your running distributed application. Starting with Aspire 9.0, MCP support has been available through manual dashboard configuration, and Aspire 13.1 added the `aspire mcp init` command for automatic setup.

It bridges the gap between your running distributed application and AI coding assistants like GitHub Copilot, Claude Code, Cursor, and OpenAI Codex.

With Aspire MCP, your AI assistant can:

- **Query resources** — Get resource states, source, endpoints, health status, and available commands
- **Debug with logs** — Access real-time console logs from any resource
- **Investigate telemetry** — Analyze structured logs and distributed traces across services
- **Execute commands** — Run resource commands directly
- **Discover integrations** — Find and understand available Aspire hosting integrations

This transforms your AI assistant from a code generator into a development partner that understands your running system.

## Two Transport Modes

Before setting up MCP, it helps to understand the two transport modes:

- **STDIO** (CLI approach) — The AI assistant launches `aspire mcp start` as a subprocess. No URL or API key needed. This is the recommended approach for Aspire 13.1+.
- **HTTP** (manual/dashboard approach) — The Aspire dashboard exposes an HTTP endpoint with URL + API key authentication. This is the approach for Aspire 9.0-13.0 or when you need more control.

## Getting Started

### Option 1: Using the Aspire CLI (Recommended)

Starting with Aspire 13.1, the `aspire mcp init` command detects supported AI assistant environments and creates the appropriate configuration files:

```bash
cd your-aspire-project
aspire mcp init
```

The command detects supported AI assistants in your environment and generates configuration files. Currently supported assistants for automatic setup:

- **Visual Studio Code** — Generates `.vscode/mcp.json`
- **GitHub Copilot CLI** — Generates Copilot CLI configuration
- **Claude Code** — Generates `.claude/` configuration
- **OpenCode** — Generates OpenCode configuration

The generated config uses STDIO transport, launching `aspire mcp start` as a subprocess. For example, Visual Studio Code gets a `.vscode/mcp.json` like:

```json
{
  "servers": {
    "aspire": {
      "type": "stdio",
      "command": "aspire",
      "args": ["mcp", "start"]
    }
  }
}
```

If you don't already have an `AGENTS.md` file in your project, one is created automatically with context about your Aspire application to help AI assistants understand your project.

### Option 2: Manual Configuration (Aspire 9.0-13.0)

For older Aspire versions, or when you need more control:

1. Run your Aspire app with `aspire run`
2. Open the Aspire dashboard
3. Click the **MCP** button in the top right corner
4. Use the displayed settings to configure your AI assistant

The dashboard provides these settings for HTTP-based MCP:

| Setting | Description |
|---------|-------------|
| `url` | Aspire MCP endpoint address |
| `type` | `http` (streamable-HTTP MCP server) |
| `x-mcp-api-key` | HTTP header for securing access |

This approach supports additional assistants including Visual Studio, Cursor, and OpenAI Codex. Consult your tool's MCP documentation for configuration details.

## MCP Tools Available

Once connected, your AI assistant gains access to several powerful tools:

### Resource Management

- **`list_resources`** — Lists all resources with state, health status, source, endpoints, and commands
- **`execute_resource_command`** — Executes commands on specific resources

### Logging and Telemetry

- **`list_console_logs`** — Gets console logs for a resource
- **`list_structured_logs`** — Retrieves structured logs, optionally filtered by resource
- **`list_traces`** — Lists distributed traces, optionally filtered by resource name
- **`list_trace_structured_logs`** — Gets structured logs for a specific trace

### Integration Discovery

- **`list_integrations`** — Shows available Aspire hosting integrations with package IDs and versions
- **`get_integration_docs`** — Retrieves documentation for a specific integration package

### AppHost Management

- **`list_apphosts`** — Lists all AppHost connections, showing which are within the working directory scope and which are outside
- **`select_apphost`** — Switches context to a specific AppHost

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

| Assistant | `aspire mcp init` | Manual (Dashboard) | Docs |
|-----------|:-----------------:|:------------------:|------|
| Visual Studio Code Copilot | ✅ | ✅ | [MCP servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) |
| GitHub Copilot CLI | ✅ | ✅ | [Add MCP server](https://docs.github.com/copilot/how-tos/use-copilot-agents/use-copilot-cli#add-an-mcp-server) |
| Claude Code | ✅ | ✅ | [MCP configuration](https://docs.claude.com/en/docs/claude-code/mcp) |
| OpenCode | ✅ | ✅ | [OpenCode docs](https://opencode.ai) |
| Visual Studio | — | ✅ | [MCP configuration](https://learn.microsoft.com/visualstudio/ide/mcp-servers) |
| Cursor | — | ✅ | [Installing MCP servers](https://cursor.com/docs/context/mcp#installing-mcp-servers) |
| OpenAI Codex | — | ✅ | [MCP setup](https://developers.openai.com/codex/mcp/) |

## Securing the API Key

When using the manual/HTTP configuration, the `x-mcp-api-key` secures access to MCP. Your AI assistant needs access to this key — use your tool's secure storage to avoid committing it to source control.

**Visual Studio Code Example** — Use [input variables](https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_input-variables-for-sensitive-data) to prompt for the key at connection time rather than hardcoding it in `mcp.json`.

> **Note:** If you're using `aspire mcp init` (STDIO transport), there's no API key to manage — authentication is handled by the subprocess communication.

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

- [Configure MCP Quick Start](https://aspire.dev/get-started/configure-mcp/)
- [Aspire MCP Server Documentation](https://aspire.dev/dashboard/mcp-server/)
- [aspire mcp init Command Reference](https://aspire.dev/reference/cli/commands/aspire-mcp-init/)
- [aspire mcp start Command Reference](https://aspire.dev/reference/cli/commands/aspire-mcp-start/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Open MCP Issues on GitHub](https://github.com/dotnet/aspire/issues?q=is%3Aopen+label%3Amcp)

## Wrapping Up

Aspire MCP represents a shift in how we interact with distributed applications during development. By giving AI assistants real-time access to your running system, you unlock debugging and development workflows that weren't possible before.

Try `aspire mcp init` in your next project and see how it transforms your AI-assisted development experience.

Until next time, happy Aspiring!

## Related Posts

- [Getting Started with the Aspire CLI](/posts/aspire-cli-getting-started/)
- [Aspire CLI Part 2 - Deployment and Pipelines](/posts/aspire-cli-part-2/)
