---
title: "Aspire Field Notes"
description: "Practical notes on using Aspire 13.6 beyond the quickstart."
draft: true
---

Aspire Field Notes is a six-post series about the parts of Aspire that matter after the first demo: a polyglot developer loop, useful resilience defaults, observability, secret handling, deployment choices, and AI-provider reliability.

The series builds on the [Aspire CLI guide](/posts/aspire-cli-getting-started/), [deployment guide](/posts/aspire-cli-part-2/), and [MCP guide](/posts/aspire-cli-part-3-mcp/). The new posts target Aspire 13.6 and distinguish stable features from preview packages and experimental APIs.

## The series

| Post                                                                                                          | Focus                                                                                                                    | Status  |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------- |
| [Aspire 13.6 AppHost Polyglot Tour](/posts/aspire-field-notes-polyglot-tour/)                                 | First-party language integrations, references versus environment settings, and the developer loop                        | Draft   |
| [Service Discovery and Resilience Defaults You Should Change](/posts/aspire-field-notes-resilience-defaults/) | Safe retries, timeout budgets, configuration migration, and comparing diagnostic runs                                    | Draft   |
| Aspire observability                                                                                          | Cross-language OpenTelemetry, 13.6 run history, the Native AOT dashboard, and Application Insights                       | Planned |
| Local secrets to Key Vault                                                                                    | Secret references, workload identity, and protecting persisted telemetry and diagnostic access                           | Planned |
| Aspire on AKS versus Container Apps                                                                           | Production trade-offs, portable volume paths, and a clearly separated look at preview Sandboxes and Express environments | Planned |
| AI provider strategy in Aspire                                                                                | Provider failure modes, Microsoft Foundry, and the migration away from retired GitHub Models                             | Planned |

Publication dates will be set after review. The earlier September and October schedule is no longer a release commitment.

## Reading behind the series

- [Maddy Montaquila's Aspire 13.6 announcement](https://devblogs.microsoft.com/aspire/whats-new-aspire-13-6/) grounds the new run-history, terminal, and hosting features.
- [David Pine's Node.js weather-map example](https://bsky.app/profile/davidpine.dev/post/3mwmut6556k2a) provides a concrete frontend/backend developer loop to explore.
- [David Fowler's developer-loop article](https://devblogs.microsoft.com/aspire/dev-loop-tribal-knowledge/) explains why resource models and repeatable operations matter to humans and agents.
- [James Newton-King's Native AOT dashboard article](https://devblogs.microsoft.com/aspire/aspire-dashboard-native-aot/) explains the 13.6 dashboard implementation without implying general Blazor Native AOT support.

Each post connects back to the themes in my **Aspire 13: One AppHost, Many Languages** talk and links to relevant code and primary documentation.
