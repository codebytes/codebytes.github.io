---
title: Building a Flexible AI Provider Strategy in .NET Aspire
date: '2025-07-06'
categories:
- Development
tags:
- dotnet
- Aspire
- AI
- Ollama
- Azure
- OpenAI
- GitHub
- GitHub Models
- Foundry
- Foundry Local
image: images/logos/dotnet-aspire-logo.png
featureImage: images/logos/dotnet-aspire-logo.png
aliases:
- /2025/07/06/aspire-with-lots-of-ai/
- /development/tools/building-a-flexible-ai-provider-strategy-in-net-aspire/
slug: building-a-flexible-ai-provider-strategy-in-net-aspire
---
{{< figure src="/images/logos/dotnet-aspire-logo.png" alt=".NET Aspire Logo" class="mx-auto" >}}

*How I architected a single codebase to seamlessly switch between Azure OpenAI, GitHub Models, Ollama, and Foundry Local without touching the API service*

When building my latest .NET Aspire application, I faced a common challenge: how do you develop and test with different AI providers without constantly rewriting your API service? The answer turned out to be surprisingly elegant - a configuration-driven approach that lets you switch between four different AI providers with zero code changes.

<!--more-->

## The Problem: A Wide Variety of AI Choices

Modern AI development presents us with a wide variety of options. You might want to:

- **Develop locally** with Ollama for offline work
- **Prototype quickly** with Microsoft's Foundry Local
- **Test cheaply** with GitHub Models' free tier
- **Deploy to production** with Azure OpenAI's enterprise features

The traditional approach would be to write separate implementations for each provider, but that leads to code duplication and maintenance headaches. Instead, I built a system that treats AI providers as interchangeable services.

## The Solution: Configuration-Driven Architecture

The key insight was to abstract the AI provider selection entirely out of the API service. Here's how it works:

```json
{
  "AI": {
    "Provider": "foundrylocal",
    "DeploymentName": "chat",
    "Model": "phi-3.5-mini"
  }
}
```

That's it. Change a few lines in your configuration, or swap configurations/environments and your entire application switches AI providers. The result is a seamless transition with no code changes, recompilation, or deployment complexities.

## The Four Pillars of AI Provider Flexibility

| Provider | Best Use Case | Free Tier | Hardware Needs | Deployment |
| :--- | :--- | :--- | :--- | :--- |
| **Azure OpenAI** | Production workloads | No | N/A (Cloud) | Cloud |
| **GitHub Models**| Prototyping & Testing | Yes (Generous) | N/A (Cloud) | Cloud |
| **Ollama** | Offline & Local Dev | Yes | Local CPU/GPU | Local |
| **Foundry Local**| Offline High-Perf Local Dev | Yes | Local CPU/GPU | Local |

### 1. Azure OpenAI - The Enterprise Choice

{{< figure src="/images/logos/azure-openai-logo.png" alt="OpenAI Logo" >}}

Azure OpenAI is my go-to for production workloads. It's reliable, scalable, and integrates seamlessly with Azure's ecosystem:

```json
{
  "AI": {
    "Provider": "azureopenai",
    "Model": "gpt-4o"
  }
}
```

**Why I choose Azure OpenAI for production:**
- Enterprise SLAs and support
- Built-in compliance and security features
- Seamless integration with Azure services
- Predictable pricing and billing

### 2. GitHub Models - The Developer's Friend

{{< figure src="/images/logos/github-logo-inverted.png" alt="GitHub Logo" >}}

[GitHub Models](https://github.com/marketplace/models) surprised me with its generous free tier and extensive model catalog. Based on community feedback and my own testing, it's proven reliable for development and staging environments.

```json
{
  "AI": {
    "Provider": "githubmodels",
    "Model": "gpt-4o-mini"
  }
}
```

**Perfect for:**
- Early development and prototyping
- Testing different models without cost commitment
- Open source projects with budget constraints
- Experimenting with cutting-edge models

### 3. Ollama - The Privacy Champion

{{< figure src="/images/ollama.png" alt="Ollama Logo" >}}

For local development and sensitive workloads, Ollama can't be beat:

```json
{
  "AI": {
    "Provider": "ollama",
    "Model": "llama3.2"
  }
}
```

**When I reach for Ollama:**
- Working on airplanes or in poor connectivity
- Handling sensitive data that can't leave the premises
- Developing features without API costs
- Testing with models that aren't available elsewhere

> **Mac Performance Note:** If you're on Apple Silicon, avoid running Ollama in Docker containers. Docker on Mac cannot access the Metal GPU due to Apple's virtualization framework limitations. Instead, install Ollama natively on macOS to take advantage of Metal GPU acceleration. This gives you significantly better performance compared to CPU-only Docker containers. The CommunityToolkit's Ollama Integration defaults to docker, though you can use a connection string to point it to a native Ollama installation.

### 4. Foundry Local - The Microsoft Stack Choice

{{< figure src="/images/logos/ai-studio-icon-color.svg" alt="Foundry Local Logo" >}}

Microsoft's [Foundry Local](https://github.com/microsoft/Foundry-Local) offers the best of both worlds - local deployment with enterprise-grade models:

```json
{
  "AI": {
    "Provider": "foundrylocal",
    "Model": "phi-3.5-mini"
  }
}
```

**Foundry Local shines when:**
- Local deployment is required but you want recent models
- You're already invested in the Microsoft AI ecosystem
- You want to leverage hardware acceleration on your machine

> **My Personal Favorite:** After testing all four providers extensively, Foundry Local running on-device has become my go-to choice for local AI development. Unlike Ollama in Docker, Foundry Local takes full advantage of your hardware - whether that's Apple Silicon's Metal GPU, NVIDIA cards, or CPU optimization. The performance is consistently excellent, and it handles the complexity of hardware acceleration automatically.

## The Architecture Behind the Magic

The beauty of this approach lies in its simplicity. The API service never knows which AI provider it's using-it just calls the abstracted AI service interface. This is all made possible by the `Microsoft.Extensions.AI` library, which provides the core `IChatClient` abstraction. The complete source code for this project is available on my [GitHub](https://github.com/chris-ayers/aspire-ai-provider-strategy).

{{< mermaid >}}
%%{init: {'theme': 'default'}}%%
graph TD
    subgraph title[Configuration-Driven AI Provider Architecture]
    A[appsettings.json] --> B{AI Provider Config};
    B --> C{AddAIServices};
    C --> D{IChatClient};
    subgraph API Service
        D --> E[Your Service Code];
    end
    subgraph Provider Implementations
        C --> F[AzureOpenAIClient];
        C --> G[OllamaApiClient];
        C --> H[GitHubModels Client];
        C --> I[FoundryLocal Client];
    end
    end
{{< /mermaid >}}

Here's how I structured it.

---

### The Secret Sauce: Configuration-Driven Service Registration

The magic happens in the `AIServiceExtensions.cs` file. A single call in `Program.cs` kicks everything off:

```csharp
// In your Program.cs
var builder = WebApplication.CreateBuilder(args);

// This one line does it all
builder.AddAIServices();
```

The `AddAIServices` extension method reads the configuration and registers the correct `IChatClient` implementation. At its heart is a simple `switch` statement that delegates to a specific registration method for each provider:

```csharp
public static IHostApplicationBuilder AddAIServices(this IHostApplicationBuilder builder)
{
    var aiSettings = AIConfiguration.GetSettings(builder.Configuration);
    builder.Services.AddSingleton(aiSettings);

    switch (aiSettings.Provider)
    {
        case AIProvider.Ollama:
            builder.AddOllamaAIServices(aiSettings);
            break;
        case AIProvider.AzureOpenAI:
            builder.AddAzureOpenAIServices(aiSettings);
            break;
        case AIProvider.GitHubModels:
            builder.AddGitHubModelsAIServices(aiSettings);
            break;
        case AIProvider.FoundryLocal:
            builder.AddFoundryLocalAIServices(aiSettings);
            break;
        default:
            throw new InvalidOperationException($"Unsupported AI provider: {aiSettings.Provider}");
    }
    return builder;
}
```

### Provider-Specific Implementations

Each provider has a slightly different setup.

**Azure OpenAI and Ollama**

For Azure OpenAI and Ollama, the setup is straightforward thanks to .NET Aspire's built-in support. A single line is enough to register the client:

```csharp
private static void AddAzureOpenAIServices(this IHostApplicationBuilder builder, AISettings aiSettings)
{
    builder.AddAzureOpenAIClient("ai-service")
           .AddChatClient(aiSettings.DeploymentName);
}

private static void AddOllamaAIServices(this IHostApplicationBuilder builder, AISettings aiSettings)
{
    builder.AddOllamaApiClient(aiSettings.DeploymentName)
           .AddChatClient();
}
```

**GitHub Models and Foundry Local**

GitHub Models and Foundry Local require a bit more manual configuration. They both use the standard `OpenAIClient` but pointed at different endpoints.

For GitHub Models, we create an `OpenAIClient` pointing to the `models.inference.ai.azure.com` endpoint:

```csharp
private static void AddGitHubModelsAIServices(this IHostApplicationBuilder builder, AISettings aiSettings)
{
    var githubToken = builder.Configuration["GITHUB_TOKEN"] ??
                      builder.Configuration["ConnectionStrings:GitHubModels"];

    builder.Services.AddSingleton<IChatClient>(serviceProvider =>
    {
        var openAIClient = new OpenAIClient(
            new System.ClientModel.ApiKeyCredential(githubToken),
            new OpenAIClientOptions { Endpoint = new Uri("https://models.inference.ai.azure.com") }
        );
        return openAIClient.GetChatClient(aiSettings.Model).AsIChatClient();
    });
}
```

For Foundry Local, the code first starts the local model server using `FoundryLocalManager` and then creates an `OpenAIClient` that points to the local endpoint it provides.

```csharp
private static void AddFoundryLocalAIServices(this IHostApplicationBuilder builder, AIConfiguration.AISettings aiSettings)
{
    builder.Services.AddSingleton<IChatClient>(serviceProvider =>
    {
        var manager = FoundryLocalManager.StartModelAsync(aliasOrModelId: aiSettings.Model).GetAwaiter().GetResult();
        var modelInfo = manager.GetModelInfoAsync(aliasOrModelId: aiSettings.Model).GetAwaiter().GetResult();

        var openAIClient = new OpenAIClient(
            new System.ClientModel.ApiKeyCredential(manager.ApiKey),
            new OpenAIClientOptions { Endpoint = manager.Endpoint }
        );
        return openAIClient.GetChatClient(modelInfo?.ModelId ?? aiSettings.Model).AsIChatClient();
    });
}
```

Your API service code remains blissfully unaware of this complexity. It simply requests an `IChatClient` and starts making calls, confident that the correct provider is handling the request.

## Real-World Switching Techniques

### Technique 1: Environment-Based Switching

My favorite approach is to use environment-specific configuration files:

```json
// appsettings.Development.json
{
  "AI": {
    "Provider": "foundrylocal",
    "Model": "phi-3.5-mini"
  }
}

// appsettings.Production.json
{
  "AI": {
    "Provider": "azureopenai",
    "Model": "gpt-4o"
  }
}
```

This means developers get fast, local AI by default, while production gets the reliability of Azure OpenAI.

### Technique 2: Feature Flag-Style Switching

Want to test a new provider with just a subset of users? Environment variables make this trivial:

```bash
# Test GitHub Models for 10% of traffic
export AI__Provider="githubmodels"
export AI__Model="gpt-4o-mini"
```

### Technique 3: Command-Line Override

Perfect for debugging or one-off tests:

```bash
dotnet run --project src/BuildWithAspire.AppHost -- --AI:Provider=ollama --AI:Model=llama3.2
```

---

## Building for Resilience: Error Handling and Health Checks

A flexible provider strategy also requires robust error handling. What happens if your primary provider goes down or a local model crashes?

I recommend implementing a few key patterns:
- **Health Checks**: Use .NET Aspire's health check features to monitor the status of your AI provider endpoints. This allows you to detect failures quickly and potentially route traffic away from an unhealthy provider.
- **Retry Policies**: Implement a retry policy (e.g., with Polly) to handle transient network issues.
- **Fallback Strategy**: For critical applications, consider a fallback mechanism. If a request to your primary provider fails, you could automatically retry with a secondary provider. This can be implemented within a custom `IChatClient` wrapper.

These strategies ensure your application remains resilient, even when individual components fail.

---

## Lessons Learned from Production

### What Works Well

**GitHub Models exceeded my expectations.** The free tier is generous, and the model selection is impressive. I've been using it for all my development work, and it's become my go-to for prototyping.

**Ollama is fantastic for air-gapped environments.** When I need to demo on a flight or work with sensitive data, Ollama ensures I'm never blocked by connectivity issues.

**Foundry Local surprised me with its performance.** While I haven't run formal benchmarks, my experience shows that first-token response times are significantly faster with Foundry Local on my machine compared to cloud-based providers. It's become my default choice for local AI development.

### What Caught Me Off Guard

**Token usage varies dramatically between providers.** The same conversation might cost 10x more on one provider than another. I learned to monitor token usage carefully, especially when switching between providers.

**Model behavior isn't always consistent.** GPT-4o on Azure OpenAI behaves slightly differently than on GitHub Models. It's not a problem, but it's worth testing your specific use cases when switching.

**Local providers need warm-up time.** Ollama and Foundry Local can take a few seconds to respond to the first request after being idle. I added a simple warm-up call during application startup.

**Mac users, beware the Docker trap.** I learned this the hard way: running Ollama in Docker on Apple Silicon is painfully slow because Docker can't access the Metal GPU. Apple's virtualization framework blocks GPU exposure to containers, so you get CPU-only performance. The solution? Run Ollama natively or use Foundry Local on macOS for Metal acceleration.

---

## The Cost-Optimization Strategy

Here's how I use different providers throughout my development lifecycle:

1. **Development:** Foundry Local or Ollama (free, fast iteration)
2. **Testing:** GitHub Models (free tier covers most testing needs)
3. **Staging:** GitHub Models or Azure OpenAI (depending on expected load)
4. **Production:** Azure OpenAI (enterprise features, SLAs)

This approach has cut my AI development costs by roughly 80% while maintaining flexibility.

---

## The One-Line Provider Switch

The most satisfying part of this architecture is how easy it is to switch providers. Whether you're responding to a service outage, testing a new model, or optimizing costs, it's always just a simple configuration change or command line override.

No code changes. No redeployment. Just a quick update and restart.

---

## A Note on Versioning

The AI landscape is evolving rapidly. For this project, I used **.NET 9** with **.NET Aspire 9.3**. If you're implementing a similar solution, be sure to check for the latest versions and any potential breaking changes.

---

## What's Next?

I'm excited about the future of AI provider flexibility. Some ideas I'm exploring:

- **Intelligent routing** based on request type or user tier
- **Cost-based switching** that automatically chooses the most economical provider
- **A/B testing** different models for the same conversation
- **Hybrid approaches** that use multiple providers for different parts of the same workflow

The configuration-driven approach makes all of these possibilities simple to implement.

---

## Final Thoughts

Building AI applications doesn't have to lock you into a single provider. With the right architecture, you can have the best of all worlds: local development, cost-effective testing, and enterprise-grade production deployment.

The key is to think of AI providers as interchangeable services from day one. Your future self will thank you when you need to switch providers for cost, performance, or compliance reasons.

*Have you built something similar? I'd love to hear about your experiences with multi-provider AI architectures. Drop me a line on [Blue Sky](https://bsky.app/profile/chris-ayers.com) or [LinkedIn](https://linkedin.com/in/chris-ayers).*

## GitHub Repositories

{{< github repo="microsoft/Foundry-Local" >}}
{{< github repo="chris-ayers/aspire-ai-provider-strategy" >}}

