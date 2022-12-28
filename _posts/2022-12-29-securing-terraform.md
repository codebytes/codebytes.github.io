---
title: Securing Terraform
type: post
categories:
- Development
tags:
- terrafrom
- security
- tools
- vscode
mermaid: true
permalink: /2022/12/29/securing-terraform
---

Securing Terraform starts before we even deploy anything. Our tooling is a great place to start! We can leverage one or more static code analyzers to look for misconfigurations, security issues, and other problems.
Many of these great tools not only plug into our CI/CD pipeline, they also work within our IDEs. This allows us to catch issues before we even commit our code.

Today we are going to look at a few of these tools and how we can leverage them to secure our Terraform code. I've included a few of my favorite tools, but there are many more out there. I encourage you to check them out and see which ones work best for you.

- [tfsec](https://github.com/aquasecurity/tfsec)
- terrascan
- checkov

## tfsec

Let's start with tfsec by aquasecurity. This is an opensource tool available on GitHub at [https://github.com/aquasecurity/tfsec](https://github.com/aquasecurity/tfsec). The docs are hosted at: [https://aquasecurity.github.io/tfsec/](https://aquasecurity.github.io/tfsec/). There are some amazing guides to installing it and configuring it for GitHub Actions.

We can run tfsec from a docker container or we can install it locally via homebrew, chocolatey, go, or the [releases page](https://github.com/aquasecurity/tfsec/releases). 