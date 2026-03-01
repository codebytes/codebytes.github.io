---
title: Dev Containers - Part 1
date: '2023-12-27'
categories:
- Development
tags:
- containers
- Docker
- DevOps
- VSCode
- GitHub
image: images/logos/dev-containers-logo.png
featureImage: images/logos/dev-containers-logo.png
aliases:
- /2023/12/27/dev-containers-part-1/
- /development/dev-containers-part-1/
slug: dev-containers-part-1
---
![dev containers](/images/logos/dev-containers-logo.svg)

> This article is part of the Festive Tech Calendar 2023. For more articles in the series by other authors, visit [https://festivetechcalendar.com/](https://festivetechcalendar.com/).

Dev Containers can revolutionize the way we approach development environments, offering a fast, consistent setup across different projects. As a developer who uses Dev Containers in VS Code for various projects, I've experienced firsthand the benefits of having an environment that's ready to go as soon as I clone a project.

I use Dev Containers in VS Code or GitHub Codespaces for all my development work. I have a Dev Container for each project I work on. This ensures that I have a consistent environment for each project. It also allows me to quickly get up and running with a new project. I don't have to worry about installing dependencies or setting up my environment. I can simply clone the project and start coding.

## What are Dev Containers?

Dev Containers, or Development Containers, are an innovative tool for modern software development. They leverage the power of containerization technology, similar to Docker, to create isolated, consistent, and fully equipped development environments. Here's what sets them apart:

![Dev Container Architecture](/images/dev-containers-architecture.png)

- **Environment Isolation**: Each Dev Container operates in its own isolated environment. This means that it can have its own set of tools, software dependencies, and settings, separate from the host machine and other containers. This isolation reduces "it works on my machine" problems, ensuring that the environment is consistent across all developers' machines.
- **Flexibility and Versatility**: Dev Containers can be tailored to support various programming languages, frameworks, and tools. They can range from simple environments with just a basic editor and runtime to more complex setups with databases, compilers, debuggers, and other tools.
- **Integration with Development Tools**: Perhaps one of the most powerful features of Dev Containers is their integration with popular development tools like Visual Studio Code. This integration allows developers to use the rich features of their favorite IDEs, like IntelliSense, debuggers, and extensions, inside the container.

## Why Use Dev Containers?

The adoption of Dev Containers in your development process can bring numerous advantages:

- **Rapid Onboarding and Consistency**: New team members can get up and running quickly. Instead of spending time setting up their development environment, they can simply pull the Dev Container configuration and start coding. This process ensures that every team member works in an environment that is consistent with production and their peers, reducing "works on my machine" issues.

- **Reproducible Environments**: Dev Containers ensure that the development environment is reproducible. This is critical when working with complex applications that require specific configurations, tools, or dependencies. With a Dev Container, these configurations are codified, making it easy to recreate the environment anytime.

- **Seamless CI/CD Integration**: Dev Containers can be integrated with Continuous Integration and Continuous Deployment (CI/CD) pipelines. This ensures that the applications are built and tested in the same environment in which they were developed, leading to fewer surprises when moving from development to production.

- **Platform Independence**: Developers can work on different operating systems or platforms without worrying about compatibility issues. The containerized environment abstracts away the underlying platform, allowing for a seamless development experience across Windows, macOS, and Linux.

- **Focus on Coding, Not Configuration**: Dev Containers abstract away the need for developers to manage their development environment. This allows developers to focus on writing code, rather than spending time configuring and troubleshooting their local setup.

## Solving Version Conflicts with Dev Containers: A Real-World Scenario

### The Challenge of Multiple Projects with Different Dependencies

In software development, it's common to work on multiple projects simultaneously. However, this can lead to significant challenges, particularly when these projects depend on different versions of languages or tools. Let's consider an example involving Python or Node.js.

Imagine working on two separate projects: Project A and Project B. Project A requires Node.js 18, while Project B needs Node.js 20. Setting up these projects on the same development machine traditionally leads to version conflicts. Installing the dependencies for Project B might break Project A, and vice versa. This is a common headache for developers, leading to a lot of time spent on managing and troubleshooting environments rather than coding.

### How Dev Containers Provide a Solution

Dev Containers offer an elegant solution to this problem. With Dev Containers, each project runs in its own isolated containerized environment. This isolation means you can have different versions of Python, Node.js, or any other dependencies in each container without them conflicting with each other

- **Isolation**: Each Dev Container provides an isolated environment. You can configure Project A's container with Node.js 18, and Project B's container with Node.js 20.
- **Consistency**: The environments remain consistent regardless of other projects. Setting up Project B won't affect Project A at all.
- **Ease of Switching**: Switching between projects is as simple as switching containers. There's no need to reconfigure your environment or worry about conflicting versions.
- **Replicability**: These containerized environments can be replicated across different machines or team members, ensuring that everyone is working in the same setup.
- **Specialized Configurations**: Dev Containers can include specific configurations for each project, such as extensions, settings, and tools.

## Real-World Applications of Dev Containers: CPython and Home Assistant

### CPython: Streamlining Python Development

The CPython project, the source code of the Python programming language itself, is an excellent example of Dev Containers in action. CPython's GitHub repository features a [`devcontainer.json`](https://github.com/python/cpython/blob/main/.devcontainer/devcontainer.json) file, which simplifies the setup process for contributors. This file specifies a Docker image tailored for Python development, ensuring that contributors have all the necessary tools and dependencies.

#### Key Features of CPython's Dev Container

- **Specific Docker Image**: The container uses an image with all dependencies required to build and test Python.
- **VS Code Extensions**: Extensions like Python, C++, and Test Explorer are pre-configured, streamlining the development experience.
- **Consistent Settings**: Settings are predefined to match the project's coding standards, ensuring consistency across all contributions.

### Home Assistant: Facilitating Smart Home Development

Home Assistant, an open-source home automation platform, also leverages Dev Containers to provide a consistent development environment. Their repository includes a [`devcontainer.json`](https://github.com/home-assistant/core/blob/dev/.devcontainer/devcontainer.json) file, which sets up an environment with all the necessary dependencies and extensions for development.

#### Advantages for Home Assistant Contributors

- **Custom Docker Image**: Ensures that all the specific requirements for developing Home Assistant are met, including the right versions of Python and other dependencies.
- **Predefined Extensions and Settings**: The Dev Container includes extensions like pylint and pylance to align with the project's development practices.
- **Ease of Contribution**: New contributors can quickly set up a development environment that is consistent with the project's standards, facilitating easier and more efficient contributions.

## Tool Support for Dev Containers

Dev Containers are supported by a range of tools and services, each enhancing the development experience in unique ways. Here's an overview of some of the key tools and integrations:

### Visual Studio Code and Dev Containers Extension

- **Integrated Development Environment**: Visual Studio Code, along with its Dev Containers extension, is a key component in the Dev Container ecosystem. It provides a full range of features for containerized development, including IntelliSense, debuggers, and various extensions.
  ![Dev Containers Extension](/images/dev-containers-extension.png)

- **Docker Integration**:
  - **Local Connection**: The extension seamlessly integrates with local Docker installations, allowing developers to easily build and manage containers on their machine.
  - **Remote Connection**: Supports connecting to Docker in remote environments, such as VMs or cloud-hosted servers, enabling development in complex, distributed architectures.
- **Enhanced Workflow**: This integration simplifies workflows by managing container lifecycles, port forwarding, and providing a consistent development environment regardless of the host system.

### GitHub Codespaces

![GitHub Codespaces](/images/dev-containers-codespaces.png)

- **Cloud-Based Environments**: Offers a range of VM options from 2 to 32 cores and up to 64 GB of memory for versatile cloud development.
- **Remote Access**: Easily accessible for coding via the browser or Visual Studio Code.
- **Quick Setup**: Features pre-configured environments for immediate project start-up and branch-specific setups from GitHub imports.
- **Editor Compatibility**: Supports various editors, including the Codespaces web editor and Visual Studio Code.
- **Customizable Configurations**: Tailor environments using `devcontainer.json`, with specific GitHub Codespaces properties.
- **Secure and Integrated**: Ensures a secure development experience in ephemeral VMs, integrated with numerous development tools.

### Visual Studio

- **C++ Project Support**: Visual Studio 2022 version 17.4 and later includes Dev Containers support for C++ projects, enhancing workflows in Linux and embedded development contexts.

### IntelliJ IDEA

- **Early Dev Containers Support**: Offers preliminary support for Dev Containers, enabling both remote operation via SSH and local usage with Docker.

### CodeSandbox

- **Web-Based and Cloud Development**: CodeSandbox offers both an online IDE for rapid web development and cloud development environments running on a microVM architecture. It supports a range of specs and multiple editors, including the CodeSandbox web editor, VS Code, and the CodeSandbox iOS app.

### DevPod

- **Flexible Environment Creation**: DevPod is a client-only tool that creates reproducible developer environments based on `devcontainer.json`, compatible with various backends such as local machines, Kubernetes clusters, remote machines, or cloud VMs.

### Dev Container CLI

- **Reference Implementation**: The Dev Container CLI acts as the standard implementation for the Dev Container Spec, facilitating the creation and management of Dev Containers, particularly in CI/DevOps scenarios.

## Building a Dev Container

You can build a Dev Container using the Command Palette in VS Code. This process involves choosing the right Dev Container for your project based on your needs.

![Dev Containers Command Palette](/images/dev-containers-add-files.png)

## Templates and Customizations

Dev Containers come with various templates and customization options:

- Templates: Choose from base templates like Alpine, Debian, Ubuntu, or focus on specific languages or tools. [Full list of templates](https://containers.dev/templates).
- Dockerfile or Docker Compose: You can use a Dockerfile or Docker Compose file to define and configure your Dev Container.
- Customizations: Include features, extensions, settings, startup tasks, and networking configurations specific to your project.

## Features

You can add various features to your Dev Container:

- CLIs for cloud platforms like Azure, GitHub, GCP, AWS.
- Tools like Terraform, Kubernetes.
- Runtimes including Node, Python, Go, Java, .NET, PHP, Ruby, Rust, C/C++, C#.
- [Full list of features](https://containers.dev/features).

## Samples

The [vscode-remote-try-\*](https://github.com/search?q=org%3Amicrosoft+vscode-remote-try-&type=Repositories) repositories include sample Dev Containers for various languages and tools. These repositories are a great place to start if you're new to Dev Containers.

- [Node Sample](https://github.com/Microsoft/vscode-remote-try-node)
- [Python Sample](https://github.com/Microsoft/vscode-remote-try-python)
- [Go Sample](https://github.com/Microsoft/vscode-remote-try-go)
- [Java Sample](https://github.com/Microsoft/vscode-remote-try-java)
- [.NET Core Sample](https://github.com/Microsoft/vscode-remote-try-dotnetcore)
- [Rust Sample](https://github.com/microsoft/vscode-remote-try-rust)
- [C++ Sample](https://github.com/microsoft/vscode-remote-try-cpp)

## Resources

Incorporating Dev Containers into your workflow can streamline development, ensuring consistency and efficiency. For more information, check out the following resources:

- [Dev Container Templates](https://containers.dev/templates)
- [Dev Container Features](https://containers.dev/features)
- [VSCode: Dev Containers Tutorial](https://code.visualstudio.com/docs/devcontainers/tutorial)
- [Beginner's Series to Dev Containers](https://learn.microsoft.com/en-us/shows/beginners-series-to-dev-containers/)
- My Talk on Dev Containers: [Codebytes/Dev-Containers](https://github.com/codebytes/dev-containers)
