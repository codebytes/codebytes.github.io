---
title: Containerizing .NET - Part 1
type: post
categories:
  - Development
tags:
  - c#
  - dotnet
  - containers
  - docker
  - devops
permalink: /2023/12/03/containerizing-dotnet-part-1
header:
  teaser: /assets/images/dotnet-logo.png
  og_image: /assets/images/dotnet-logo.png
excerpt_separator: <!--more-->
---

![.NET]({{ site.url }}{{ site.baseurl }}/assets/images/dotnet-logo.png)

> This article is part of C# Advent 2023. For more articles in the series by other authors, visit [https://www.csadvent.christmas/](https://www.csadvent.christmas/).

This is the first in a series of articles on containerizing .NET applications. We'll explore how to containerize .NET applications using Dockerfiles and `dotnet publish`. Containers have become an essential part of the DevOps ecosystem, offering a lightweight, portable, and scalable solution for deploying applications. This process is crucial for developers looking to streamline app deployment in containerized environments, focusing on efficiency, security, compliance, and more.

You can read the series of articles here:

- [Containerizing .NET: Part 1 - A Guide to Containerizing .NET Applications](/2023/12/03/containerizing-dotnet-part-1)
- [Containerizing .NET: Part 2 - Considerations](/2024/2/19/containerizing-dotnet-part-2)

## What are Containers?

Containers are a lightweight, virtualized environment that provide an isolated space for running applications. Unlike traditional virtual machines that require a full-fledged operating system, containers share the host system's kernel but encapsulate an application's code, dependencies, and libraries in a self-contained unit. This encapsulation ensures uniform and consistent application performance across different computing environments.

Containers offer numerous benefits. They are efficient in terms of resource utilization, smaller in size, and require less overhead than virtual machines. Containers also enhance the portability of applications, enabling developers to easily move applications from local development machines to production servers. This portability, combined with their isolated nature, facilitates continuous integration and continuous deployment (CI/CD) practices, making containers a cornerstone of modern DevOps workflows. Moreover, containers help ensure software runs reliably when moved from one computing environment to another, mitigating the "it works on my machine" problem.

## Dotnet with a Dockerfile

Building and packaging dotnet applications into Docker images has been straightforward and well-documented. The [dotnet documentation](https://learn.microsoft.com/en-us/dotnet/core/docker/build-container?tabs=linux&pivots=dotnet-8-0) provides an excellent starting point. A simple Dockerfile can build a dotnet application and package it into a Docker image, using multi-stage builds to keep the final image size small.

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env
WORKDIR /App

# Copy everything
COPY . ./
# Restore as distinct layers
RUN dotnet restore
# Build and publish a release
RUN dotnet publish -c Release -o out

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /App
COPY --from=build-env /App/out .
ENTRYPOINT ["dotnet", "DotNet.Docker.dll"]
```

We can build this docker image by running the following command, where `dotnet-docker` is the name of the image.

```bash
docker build -t dotnet-docker .
```

I won't go into all the details of a dockerfile or registries right now. We'll cover that in a future article. However, while this approach is great for those wanting full control over the image-building process, it can be daunting for newcomers to containers or those who prefer to focus on building applications rather than managing Docker images.

## Containerizing .NET with dotnet publish

.NET has a built-in mechanism for building and packaging applications into Docker images. This approach is ideal for those who want to focus on application development rather than managing Docker images. We'll explore how to containerize .NET applications using `dotnet publish`. This method doesn't require a Dockerfile. Instead, it uses a set of publish properties to build and package applications into Docker images.

Starting from scratch, we'll containerize a simple dotnet application using the dotnet CLI.

1. Create a new dotnet console application

```bash
dotnet new console -o hello-containers
```

1. Let's add the required nuget package, Microsoft.NET.Build.Containers

```bash
dotnet add package Microsoft.NET.Build.Containers
```

1. Now we can build and package our application into a docker image

```bash
dotnet publish -t:PublishContainer
```

At this point you should see something like the following:

```bash
MSBuild version 17.8.3+195e7f5a3 for .NET
  Determining projects to restore...
  All projects are up-to-date for restore.
  hello-containers -> /workspaces/dotnet-containers/hello-containers/bin/Release/net8.0/hello-containers.dll
  hello-containers -> /workspaces/dotnet-containers/hello-containers/bin/Release/net8.0/publish/
  Building image 'hello-containers' with tags 'latest' on top of base image 'mcr.microsoft.com/dotnet/runtime:8.0'.
  Pushed image 'hello-containers:latest' to local registry via 'docker'.
```

Notice that we didn't have to create a Dockerfile, we didn't have to manage dependencies, and we didn't have to package our application into a docker image.
Let's compare the docker image we just created with the one we created earlier. The following is the docker image we created earlier using a Dockerfile.

```bash
$ docker images
REPOSITORY         TAG       IMAGE ID       CREATED          SIZE
hello-containers   latest    83963b52892f   5 seconds ago    193MB
dotnet-docker      latest    2d24bdc0b15d   57 seconds ago   217MB
```

## Making it Smaller

To make our images smaller, we have a few options. The first is to choose a smaller base image. Popular choices include Alpine, a lightweight Linux distribution, and Ubuntu Chiseled, a lightweight version of Ubuntu. Using these base images can significantly reduce the final image size.

By introducing the `-p:ContainerFamily` parameter, we can specify the image family; And the `-p:ContainerRepository` parameter we can name our image. By leveraging image families like Alpine and Ubuntu Chiseled, we can significantly reduce the final image size without trimming or optimizing via Native AOT (Ahead of Time compilation). We'll cover those optimization techniques in a future article.

## Alpine

Alpine Linux is a highly favored choice for container images, known for its lightweight nature and security-focused architecture. Its minimal footprint significantly enhances efficiency in resource usage, making it ideal for streamlined container images. This results in reduced overhead and improved performance in containerized applications. However, it's important to consider certain aspects when using Alpine:

- Resource Optimization: Alpine's small size optimizes resource consumption.
- Compliance: Minimal dependencies make it compliance-friendly.
- Compatibility Note: Alpine uses musl libc instead of glibc, potentially leading to compatibility issues with glibc-dependent applications.

When using dotnet publish to containerize an application with Alpine, you can specify the container family as alpine to use this lightweight base image:

```bash
$ dotnet publish -t:PublishContainer -p:ContainerFamily=alpine -p:ContainerRepository=hello-containers-alpine
MSBuild version 17.8.3+195e7f5a3 for .NET
  Determining projects to restore...
  All projects are up-to-date for restore.
  hello-containers -> /workspaces/dotnet-containers/hello-containers/bin/Release/net8.0/hello-containers.dll
  hello-containers -> /workspaces/dotnet-containers/hello-containers/bin/Release/net8.0/publish/
  Building image 'hello-containers-alpine' with tags 'latest' on top of base image 'mcr.microsoft.com/dotnet/runtime:8.0-alpine'.
  Pushed image 'hello-containers-alpine:latest' to local registry via 'docker'.
```

The resulting base image, mcr.microsoft.com/dotnet/runtime:8.0-alpine, is smaller compared to the standard mcr.microsoft.com/dotnet/runtime:8.0. Here's a comparison of image sizes:

```bash
$ docker images
REPOSITORY                TAG       IMAGE ID       CREATED          SIZE
hello-containers-alpine   latest    60a63389d474   18 seconds ago   82.7MB
hello-containers          latest    ae96d4d7ac36   23 seconds ago   193MB
```

This demonstrates that Alpine can significantly reduce image size, enhancing the efficiency of .NET containerized applications.

## Ubuntu Chiseled

Ubuntu Chiseled is a lightweight, container-optimized version of the popular Ubuntu Linux distribution. Featuring ultra-small OCI images, it includes only the application and its runtime dependencies, leading to several key benefits:

- Streamlined Design: The reduced footprint of Ubuntu Chiseled images enables lightweight maintenance and efficient resource utilization.
- Enhanced Security: The focus on essential components minimizes security risks by reducing potential vulnerabilities.
- Size Reduction: Compared to traditional Ubuntu images, Chiseled images are significantly smaller, comparable in size to Alpine, and offer glibc compatibility.
- Fewer Components: With fewer components, there's a reduced CVE exposure, aligning well with development and production environments.
- Strong Support: Developed through a collaboration between Canonical and Microsoft, these images offer robust support, particularly suitable for .NET versions 6, 7, and 8.

![.NET]({{ site.url }}{{ site.baseurl }}/assets/images/ubuntu-chiseled.png)

The following example demonstrates containerizing a .NET application using Ubuntu Chiseled, showcasing the notable reduction in image size:

```bash
$ dotnet publish -t:PublishContainer -p:ContainerFamily=jammy-chiseled -p:ContainerRepository=hello-containers-chiseled
MSBuild version 17.8.3+195e7f5a3 for .NET
  Determining projects to restore...
  All projects are up-to-date for restore.
  hello-containers -> /workspaces/dotnet-containers/hello-containers/bin/Release/net8.0/hello-containers.dll
  hello-containers -> /workspaces/dotnet-containers/hello-containers/bin/Release/net8.0/publish/
  Building image 'hello-containers-chiseled' with tags 'latest' on top of base image 'mcr.microsoft.com/dotnet/runtime:8.0-jammy-chiseled'.
  Pushed image 'hello-containers-chiseled:latest' to local registry via 'docker'.
```

Notice how the base image was changed from `mcr.microsoft.com/dotnet/runtime:8.0` to `mcr.microsoft.com/dotnet/runtime:8.0-jammy-chiseled`. This is a smaller base image, which results in a smaller final image. Let's take a look at the size difference between the images.

```bash
$ docker images
REPOSITORY                  TAG       IMAGE ID       CREATED          SIZE
hello-containers-chiseled   latest    bfdb924079ab   6 seconds ago    85.7MB
hello-containers-alpine     latest    cde2172a1f17   6 minutes ago    82.7MB
hello-containers            latest    83963b52892f   16 minutes ago   193MB
dotnet-docker               latest    2d24bdc0b15d   17 minutes ago   217MB
```

The comparison illustrates how Ubuntu Chiseled effectively reduces the container image size, making it an efficient choice for cloud and containerized environments.

## **Streamlining with Project File Properties**

Streamlining the deployment process in .NET can be achieved by integrating publish properties directly into the project file. This approach enhances compliance and security while reducing the likelihood of errors. Consider a typical .csproj file:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Build.Containers" Version="8.0.100" />
  </ItemGroup>

</Project>
```

To streamline, we add container-specific properties directly into the .csproj:

```xml
<PropertyGroup>
  <!-- Existing properties -->
  <ContainerFamily>jammy-chiseled</ContainerFamily>
  <ContainerRepository>hello-containers-chiseled</ContainerRepository>
</PropertyGroup>
```

Our final csproj file looks like this:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <ContainerFamily>jammy-chiseled</ContainerFamily>
    <ContainerRepository>hello-containers-chiseled</ContainerRepository>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Build.Containers" Version="8.0.100" />
  </ItemGroup>
```

With these additions, the deployment command simplifies to:

```bash
dotnet publish -t:PublishContainer
```

This method eliminates the need to specify publish properties each time, as they are already defined in the project file. It ensures a consistent and repeatable process, making deployments smoother and more efficient.

## Conclusion

Publishing .NET console apps as container images offers a range of options, like targeting specific Linux distributions or families. Each method has unique benefits in terms of size, security, compliance, composability, compatibility, and support. This approach signifies a move towards more specialized, purpose-built container images, shaping the future of cloud applications.

Thank you for joining me on this exploration of .NET and containers. Stay tuned for more insights and guides on containerizing .NET!

## Resources

- [https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-8#containers](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-8#containers)
- [https://learn.microsoft.com/en-us/dotnet/core/docker/build-container](https://learn.microsoft.com/en-us/dotnet/core/docker/build-container)
- [https://learn.microsoft.com/en-us/dotnet/core/docker/publish-as-container](https://learn.microsoft.com/en-us/dotnet/core/docker/publish-as-container)
- [https://devblogs.microsoft.com/dotnet/announcing-dotnet-chiseled-containers/](https://devblogs.microsoft.com/dotnet/announcing-dotnet-chiseled-containers/)
- [https://canonical.com/blog/chiselled-ubuntu-ga](https://canonical.com/blog/chiselled-ubuntu-ga)
- [https://ubuntu.com/containers/chiselled/dotnet](https://ubuntu.com/containers/chiselled/dotnet)
