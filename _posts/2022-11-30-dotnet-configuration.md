---
title: Validating DotNet Configuration
type: post
categories:
- DevOps
tags:
- github
- Azure DevOps
- ci/cd
permalink: /2022/11/30/validating-dotnet-configuration
---

One of the great things about the configuration system in .NET is the type safety, dependency injection, and model binding. Something we can take advantage of is to validate our configuration on startup and fail if it doesn't pass validation. Having that fast failure is awesome when working with containers and applications that have liveness and readiness probes.

How do we do this?

w