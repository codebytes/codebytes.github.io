---
title: Secure Terraform - Part 4 - checkov
type: post
categories:
- DevOps
tags:
- terraform
- security
- tools
- vscode
- checkov
- github
mermaid: true
permalink: /2023/03/24/secure-terraform-part4-checkov
header:
  teaser: /assets/images/checkov-logo.png
  og_image: /assets/images/checkov-logo.png
---

This is part 4 of the Secure Terraform series. You can read the series of articles here:

- [Secure Terraform - Part 1 - tfsec](/2022/12/29/secure-terraform-part1-tfsec)
- [Secure Terraform - Part 2 - tfsec customization](/2023/01/29/secure-terraform-part2-tfsec-customization)
- [Secure Terraform - Part 3 - terrascan](/2023/03/22/secure-terraform-part3-terrascan)
- [Secure Terraform - Part 4 - checkov](/2023/03/24/secure-terraform-part4-checkov)
- [Secure Terraform - Part 5 - terraform state](/2023/04/05/secure-terraform-part5-terraform-state)

## Introduction

In this fourth installment of our Secure Terraform series, we'll discuss Checkov, a powerful open-source static code analysis tool supported by Bridgecrew. Checkov supports Terraform, Kubernetes, Dockerfiles, AWS CloudFormation, and other Infrastructure as Code (IaC) frameworks. It focuses on security best practices, policy compliance, and industry standards. You can find Checkov's documentation and samples at [https://www.checkov.io/](https://www.checkov.io/).

![checkov-logo](/assets/images/checkov-logo.png)

## Checkov Installation and CLI

Checkov can be easily installed using pip, a package installer for Python:

``` pip install checkov ```

Alternatively, you can install Checkov using Docker:

``` docker pull bridgecrew/checkov ```

Once installed, Checkov provides a command-line interface (CLI) to scan your IaC files. To scan your Terraform code, navigate to your project's root directory and run the following command:

``` checkov -d . ```

Checkov will then analyze your Terraform files, checking for security and compliance issues. It will output the results, including the test status (PASSED or FAILED), file paths, resource types, and relevant information about the issue.

{% include figure image_path="assets/images/checkov.png" alt="checkov" caption="checkov" %}

You can customize the output format using the --output flag. Checkov supports various output formats, including JSON, JUnit XML, and SARIF:

``` checkov -d . --output json ```

## Checkov extensions for VS Code

Checkov provides extensions for VS Code and other IDEs, allowing you to scan your Terraform code directly from your code editor. This is a convenient way to scan your code as you write it, ensuring that you don't introduce any security or compliance issues.

To install the Checkov extension for VS Code, search for "Checkov" in the Extensions tab or install it from the [marketplace](https://marketplace.visualstudio.com/items?itemName=Bridgecrew.checkov).

{% include figure image_path="/assets/images/checkov-vscode.png" alt="checkov-vscode" caption="checkov-vscode" %}

You can scan your code and view the results in the Checkov Output tab. You can also view the results in the Problems tab, which provides a convenient way to navigate to the specific line of code that caused the issue.

{% include figure image_path="/assets/images/checkov-vscode-output.png" alt="checkov-vscode-output" caption="checkov-vscode-output" %}

And if you hold your cursor over the issue, you can see the violations and links to the related checks.

{% include figure image_path="/assets/images/checkov-vscode-problems.png" alt="checkov-vscode-problems" caption="checkov-vscode-problems" %}

If you click on the check, you'll get a pop-up and follow the link to the Checkov documentation.

{% include figure image_path="/assets/images/checkov-vscode-check.png" alt="checkov-vscode-check" caption="checkov-vscode-check" %}

{% include figure image_path="/assets/images/checkov-vscode-check-doc.png" alt="checkov-vscode-check-doc" caption="checkov-vscode-check-doc" %}

This is an amazing developer experience, allowing you to scan your code as you write it and fix any issues immediately.

## Checkov in CI/CD Pipelines

Integrating Checkov into your CI/CD pipeline helps ensure that your infrastructure is secure and compliant with every code change. Here's an example of how to integrate Checkov into a GitHub Actions pipeline:

```yaml
name: Checkov
on:
  push:
    branches:
      - main
jobs:
  build:

    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python 3.8
        uses: actions/setup-python@v1
        with:
          python-version: 3.8
      - name: Test with Checkov
        id: checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: example/examplea
          framework: terraform 
```

This example workflow triggers on push and pull_request events for the main branch. It checks out the repository, sets up Python, installs Checkov, and runs a scan on the specified Terraform files.

## Custom Policies and Suppressions

Checkov supports custom policies written in Python or Yaml. You can create a custom policy by following these steps:

1. Create a new directory for your custom policies, e.g., custom_policies.
2. Inside the custom_policies directory, create a new Python or Yaml file for your custom rule, e.g., my_custom_rule.py or my_custom_rule.yaml.
3. Write your custom rule using Python or the Yaml language. Refer to the Checkov documentation for guidance on writing custom policies.

In addition to custom policies, Checkov allows you to suppress specific checks or resources using inline comments in your Terraform code.

This can be useful when you want to exclude certain resources from specific checks. To suppress a check, add the following comment above the resource block:

```hcl
# checkov:skip=CKV_AZURE_123:This check is not applicable for this resource
resource "azurerm_storage_account" "example" {
  # ...
}
```

In this example, the CKV_AZURE_123 check will be skipped for the azurerm_storage_account resource with a reason "This check is not applicable for this resource."

## Conclusion

Checkov serves as a robust tool to bolster the security and compliance of your Terraform code. By seamlessly integrating Checkov into your development workflow, CI/CD pipeline, and leveraging it with your code editor, you can proactively tackle potential security risks and policy violations during the development stage itself.

The adaptability of Checkov, with its support for custom policies and the ability to selectively suppress checks, empowers organizations to customize the tool to align with their specific security objectives.

Utilizing tools like Checkov, along with others like tfsec and Terrascan, plays a pivotal role in creating and sustaining a secure and compliant infrastructure in today's rapidly evolving landscape, where Infrastructure as Code has become a fundamental component of modern development practices.
