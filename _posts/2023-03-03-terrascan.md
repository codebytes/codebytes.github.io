---
title: Secure Terraform - Part 3 - terrascan
type: post
categories:
- Development
tags:
- terraform
- security
- tools
- vscode
- terrascan
- github
mermaid: true
permalink: /2023/03/03/secure-terraform-part3-terrascan
---

This is part 3 of the Secure Terraform series. You can read the series of articles here: 
- [Secure Terraform - Part 1 - tfsec](/2022/12/29/secure-terraform-part1-tfsec) 
- [Secure Terraform - Part 2 - tfsec](/2023/01/29/secure-terraform-part2-tfsec-customization)
- [Secure Terraform - Part 3 - terrascan](/2023/03/03/secure-terraform-part3-terrascan)

# Secure Terraform - Part 3 - terrascan

Terrascan is another great tool for terraform security from Bridgecrew.

Terrascan is an open-source static code analysis tool for security compliance of your Infrastructure as Code (IaC). It has rules for various platforms, including Kubernetes, Dockerfile, AWS, Azure, GCP, and Terraform. It is built in GoLang and has a CLI, API, and Jenkins plugin. Terrascan can be used to scan your IaC files for security vulnerabilities and policy violations. It can help you identify security issues before you deploy your code, and it can also help you enforce compliance policies.

## Terrascan CLI

In addition to tfsec, there is another static code analysis tool for Terraform called Terrascan. Terrascan is open source and supported by tenable. It is also available as a VSCode extension.

You can download the Terrascan CLI from the official website: https://github.com/tenable/terrascan/releases. It is available for Windows, macOS, and Linux.

Once you have the Terrascan CLI installed, you can use it to scan your Terraform code. Terrascan comes with a number of pre-built policies that you can use. Policies define a set of rules that you want to enforce on your Terraform code. You can also create your own custom policies.

To scan your Terraform code using Terrascan, navigate to the root directory of your project and run the following command:

`terrascan scan`

By default, Terrascan will scan all Terraform files in the current directory and its subdirectories. You can specify a different directory by passing the `--path` option:

`terrascan scan --path=path/to/terraform/files`

Terrascan will output a list of violations that it found in your code. Each violation will have a rule ID, a description, and a severity level. The severity level can be either HIGH, MEDIUM, or LOW. The output will also include the filename, line number, and column number where the violation was found.

You can specify a different output format using the `--format` option. Terrascan supports a number of output formats, including JSON, YAML, and JUnit. Here's an example of how to output the results in JSON format:

`terrascan scan --format=json > output.json`

You can also specify a policy path using the `--policy-path` option. By default, Terrascan will use the policies that are included with the tool. However, you can also use your own custom policies by specifying a policy path:

`terrascan scan --policy-path=path/to/policies`

Terrascan also supports scanning remote Terraform modules. You can use the `--remote` option to scan a remote module:

`terrascan scan --remote=github.com/accurics/terrascan`

Terrascan supports a number of other options and flags that you can use. You can view the full list of options by running `terrascan help scan`.

