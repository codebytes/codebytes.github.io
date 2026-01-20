---
title: Stir Trek 2025 and Multiple Dev Containers
date: '2025-05-04'
categories:
- Development
tags:
- Copilot
- ChatGPT
- dev-containers
- codespaces
- docker-compose
image: images/stirtrek-logo.png
featureImage: images/stirtrek-logo.png
aliases:
- /2025/05/04/stir-trek-and-multiple-dev-containers/
- /ai/dev containers/codespaces/stir-trek-and-multiple-dev-containers/
slug: stir-trek-and-multiple-dev-containers
---
{{< figure src=\"/images/stirtrek-logo.png\" alt=\"Stir Trek 2025\" >}}

This month at Stir Trek 2025, I presented on Dev Containers and GitHub Codespaces, demonstrating how these tools streamline both local and cloud-based development workflows. The session covered the essentials of creating portable development environments, customizing containers with features and extensions, and launching Codespaces directly from your repository. A lively Q&A followed, with attendees asking about strategies for running and working with multiple containers. Below, I've distilled those discussions and provided a deeper dive into shared container configurations across multiple projects-including folder structures, Docker Compose setups, VS Code workflows, and advanced tips you can apply in your own work.

## Recap: Dev Containers and Codespaces

![Dev Containers](/images/dev-containers-logo.png)

Dev Containers are Docker-based environments enriched with development-specific tooling, settings, and startup tasks as defined in a `devcontainer.json` file. They enable you to use a container as a full-featured development environment-isolating dependencies, standardizing tool versions, and enabling reproducible setups locally or remotely ([Dev Containers][1]).

GitHub Codespaces builds on Dev Containers by providing cloud-hosted environments that spin up in seconds with configurable CPU, memory, and storage. Codespaces leverages the same open specification as Dev Containers, making your `devcontainer.json` a first-class citizen whether you connect via VS Code, IntelliJ, or directly in the browser ([GitHub Docs][2]).

## Q&A: Running Multiple Containers

### Can I connect to multiple containers at once?

By default, **VS Code allows only one container per window**, but you can open additional windows and attach each to a different container to work on multiple services in parallel ([Visual Studio Code][3]).

### What about using a single window for multiple containers?

![Docker Compose](/images/docker-compose-logo.png)

If you use **Docker Compose**, define multiple services in your `docker-compose.yml` and create separate `devcontainer.json` configurations for each service-each referencing the common Compose file. VS Code will then list each configuration in its Dev Container picker, letting you reopen the current window to connect to a different service without duplicating your Compose setup ([Dev Containers][4]).

### How do I configure separate containers for multiple projects?

To maintain isolation and clarity, place each container configuration in its own subdirectory under `.devcontainer`, following the pattern `.devcontainer/<project>/devcontainer.json`. Tools supporting the spec recognize this layout and list all found configurations in the Codespaces or VS Code Dev Container dropdown ([containers.dev][5], [GitHub Docs][2]).

## Shared `.devcontainer` Folder Structure

Centralize your container configurations in a single root directory:

```plaintext
dev-container/
├─ .devcontainer/
│  ├─ .env
│  ├─ docker-compose.yml
│  ├─ project-a-node-js/
│  │   └─ devcontainer.json
│  ├─ project-b-node-js/
│  │   └─ devcontainer.json
│  ├─ project-c-python/
│  │   └─ devcontainer.json
│  └─ project-d-go-lang/
│       └─ devcontainer.json
├─ project-a-node-js/
├─ project-b-node-js/
├─ project-c-python/
└─ project-d-go-lang/
```

This layout lets all projects share a **single** Compose definition and environment variables-reducing duplication and easing updates ([containers.dev][5]).

## Common Docker Compose File

In `.devcontainer/docker-compose.yml`, define every project service alongside shared dependencies:

```yaml
services:
  project-a-node-js:
    image: mcr.microsoft.com/devcontainers/base:latest
    volumes:
      - ..:/workspaces:cached
    ports:
      - "8001:8000"
    command: sleep infinity

  project-b-node-js:
    image: mcr.microsoft.com/devcontainers/base:latest
    volumes:
      - ..:/workspaces:cached
    ports:
      - "8002:8000"
    depends_on:
      - postgres

  project-c-python:
    image: mcr.microsoft.com/devcontainers/base:latest
    volumes:
      - ..:/workspaces:cached
    ports:
      - "8003:8000"
    depends_on:
      - postgres

  project-d-go-lang:
    image: mcr.microsoft.com/devcontainers/base:latest
    volumes:
      - ..:/workspaces:cached
    ports:
      - "8004:8000"

  postgres:
    image: postgres:latest
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

Each service listens on port 8000 internally and is mapped to a unique host port (8001-8004) to prevent collisions ([Visual Studio Code][6]).

## Workspace Mounts & Folder Mapping

Mounting the root-level folder into `/workspaces` in each container gives uniform access to all projects. In each `devcontainer.json`, point `workspaceFolder` at the specific subdirectory:

```json
"workspaceFolder": "/workspaces/project-b-node-js"
```

This ensures your editor is scoped appropriately when connected ([Dev Containers][4]).

## Per-Project `devcontainer.json`

Each project's configuration references the shared Compose file and specifies its service:

```jsonc
{
  "name": "Project B Dev Container",
  "dockerComposeFile": ["../docker-compose.yml"],
  "service": "project-b-node-js",
  "workspaceFolder": "/workspaces/project-b-node-js",
  "shutdownAction": "none"
}
```

Using `"shutdownAction": "none"` keeps all containers running when you close one window, so you don't inadvertently tear down shared services ([Dev Containers][7]).

## Building & Switching Between Containers

1. **Open the root folder** (`dev-container/`) in VS Code.
2. **Reopen in Container:** Run **Dev Containers: Reopen in Container** and select your desired project.
3. **Switch Container:** Later, use **Dev Containers: Switch Container** to hop to another project without restarting the Docker stack ([Visual Studio Code][3], [GitHub Docs][2]).

## Advanced Multi-Project Strategies

### Environment-Specific Overrides

Layer additional Compose files for environment-specific tweaks:

```bash
docker-compose -f docker-compose.yml \
  -f docker-compose.override.yml \
  -f docker-compose.dev.yml up -d
```

Overrides can redefine images, ports, mounts, or feature flags per environment ([Visual Studio Code][6]).

### Isolated Networks & Namespaces

Define separate Docker networks to segment traffic:

```yaml
networks:
  dev-a: {}
  dev-b: {}

services:
  project-a-node-js:
    networks: [dev-a]
  project-b-node-js:
    networks: [dev-b]
  postgres:
    networks: [dev-a, dev-b]
```

This prevents unintended inter-service communication between project environments ([Visual Studio Code][6]).

## GitHub Codespaces Integration

Codespaces recognizes the same `.devcontainer` layout:

* **Configuration Dropdown:** Multiple `devcontainer.json` files under `.devcontainer/` are automatically listed when creating a Codespace ([GitHub Docs][2]).
* **Port Forwarding:** Host-mapped ports (8001-8004) surface as forwarded ports in the Codespaces UI.
* **Pre-builds & Secrets:** Enable pre-builds in `devcontainer.json` and leverage repository or organization secrets instead of a local `.env` file ([The GitHub Blog][8]).

## Lifecycle Customization

Use Dev Container lifecycle hooks per project to automate setup:

```jsonc
"postCreateCommand": "cd /workspaces/project-a-node-js && npm ci",
"postStartCommand": "npm run migrate",
"initializeCommand": "git submodule update --init"
```

These commands ensure each container is fully prepared for development immediately ([Dev Containers][7]).

## Troubleshooting Tips

* **Stuck at "Rebuilding container..."**: Clear the Docker build cache or raise VS Code's Docker logging level.
* **Ports not forwarding:** Verify `forwardPorts` in `devcontainer.json` or check Codespaces port settings.
* **Volume performance issues:** On macOS/Windows, consider isolating cache directories (e.g., `node_modules`) in named volumes to speed up I/O ([Some Natalie's corner of the internet][9], [pamela fox's blog][10]).

## Conclusion

By centralizing Dev Container configurations and sharing a unified `docker-compose.yml`, you eliminate duplication, streamline dependency management, and enable seamless switching between multiple projects-both locally and in GitHub Codespaces. This pattern scales from a handful of services to extensive microservice landscapes, delivering consistent, reproducible developer environments across your entire workspace.

[1]: https://devcontainers.github.io/ "Development containers"
[2]: https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers "Introduction to dev containers - Codespaces - GitHub Docs"
[3]: https://code.visualstudio.com/remote/advancedcontainers/connect-multiple-containers "Connect to multiple containers - Visual Studio Code"
[4]: https://devcontainers.github.io/guide/dockerfile "Using Images, Dockerfiles, and Docker Compose"
[5]: https://containers.dev/implementors/spec/ "Development Container Specification"
[6]: https://code.visualstudio.com/docs/containers/docker-compose "Use Docker Compose - Visual Studio Code"
[7]: https://devcontainers.github.io/implementors/json_reference/ "Dev Container metadata reference"
[8]: https://github.blog/news-insights/product-news/codespaces-multi-repository-monorepo-scenarios/ "Codespaces for multi-repository and monorepo scenarios"
[9]: https://some-natalie.dev/blog/multiservice-devcontainers/ "Securing Devcontainers (part 2) - multi-service applications with ..."
[10]: https://blog.pamelafox.org/2024/11/making-dev-container-with-multiple-data.html "Making a dev container with multiple data services - pamela fox's blog"
