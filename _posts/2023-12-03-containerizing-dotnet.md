---
title: Containerizing .NET
type: post
categories:
- Development
tags:
- c#
- dotnet
- containers
- docker
- devops
permalink: /2023/12/03/containerizing-dotnet
header:
  teaser: /assets/images/dotnet-logo.png
  og_image: /assets/images/dotnet-logo.png
excerpt_separator: <!--more-->
---

![.NET]({{ site.url }}{{ site.baseurl }}/assets/images/dotnet-logo.png)

# Containerizing .NET: Part 1 - A Guide to Dockerizing .NET Applications

> This article is my entry as part of C# Advent 2023. Visit [https://www.csadvent.christmas/](https://www.csadvent.christmas/) more articles in the series by other authors.

This is the first in a series of articles on containerizing .NET applications. In this article, we'll explore how to containerize .NET applications using Dockerfiles and `dotnet publish`. Containers have become an integral part of the DevOps ecosystem. They offer a lightweight, portable, and scalable solution for deploying applications. This process is crucial for developers looking to streamline their app deployment in containerized environments, focusing on efficiency, security, compliance, and more. 

## What are Containers?

Containers are a form of lightweight, virtualized environment that provide an isolated space for running applications. Unlike traditional virtual machines that require their own full-fledged operating system, containers share the host system's kernel but encapsulate an application's code, dependencies, and libraries in a self-contained unit. This encapsulation ensures that the application runs uniformly and consistently across different computing environments.

The use of containers offers numerous benefits. They are highly efficient in terms of resource utilization, as they are smaller in size and require less overhead than virtual machines. Containers also enhance the portability of applications, enabling developers to easily move applications from local development machines to production servers. This portability, combined with their isolated nature, facilitates continuous integration and continuous deployment (CI/CD) practices, making containers a cornerstone of modern DevOps workflows. Moreover, containers help ensure that software runs reliably when moved from one computing environment to another, mitigating the "it works on my machine" problem that developers often encounter.

Before I get to all of the new .NET containerization features, let's take a look at how we used to containerize .NET applications.

## Dotnet with a Dockerfile

We've been able to build and package dotnet applications into docker images for a while now. The process is straightforward and well documented. The [dotnet documentation](https://learn.microsoft.com/en-us/dotnet/core/docker/build-container?tabs=linux&pivots=dotnet-8-0) provides a great starting point for those looking to containerize their dotnet applications. The following is a simple Dockerfile that builds a dotnet application and packages it into a docker image. 
This example uses multi-stage builds to keep the final image size small. The first stage builds the application and the second stage packages the application into a docker image.

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

Building this docker image is as simple as running the following command:

```bash
docker build -t dotnet-docker .
```

But this image leaves a lot to be desired. It's a larger image, the default user is root, and could be more secure. There are a lot of things we can do to improve this image. This requires knowing how to build Dockerfiles, manage dependencies, and package applications into docker images. This is a great option for those who want to build their own images and have full control over the process. However, this can be a daunting task for those who are new to containers or those who want to focus on building applications and not managing docker images.

Let's take a look at some of the other options we have for building and packaging dotnet applications into docker images.

## Containerizing .NET with dotnet publish

Let's start from scratch and containerize a simple dotnet application. We'll use the dotnet CLI to build and package our application into a docker image. We won't be using a Dockerfile, instead we'll use the `dotnet publish` command to build and package our application into a docker image. This is a great option for those who want to focus on building applications and not managing docker images.

1. Create a new dotnet console application
```bash
dotnet new console -o hello-containers
```

2. Let's add the required nuget package, Microsoft.NET.Build.Containers
```bash
dotnet add package Microsoft.NET.Build.Containers
```

3. Now we can build and package our application into a docker image
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

## Making it smaller

There are a few options to make our images smaller, let's take a look at some of them. The first is picking a smaller base image. The base image is the image that our application is built on top of. The base image we used in the previous example was `mcr.microsoft.com/dotnet/runtime:8.0`. This is a great base image for running dotnet applications, but it's not the smallest base image. A popular one is alpine, which is a lightweight linux distribution. But there is also Ubuntu Chiseled, which is a lightweight version of Ubuntu. Let's take a look at how we can use these base images to make our images smaller.

### Alpine

I'm going to introduce 2 new arguments... `-p:ContainerFamily` and `-p:ContainerRepository`. These arguments allow us to specify the image family we want to use (like alpine or jammy-chiseled) and the name of the image we want to create. Let's take a look at how we can use these arguments to create a smaller image.

```bash
$ dotnet publish -t:PublishContainer -p:ContainerFamily=alpine /p:ContainerRepository=hello-containers-alpine
MSBuild version 17.8.3+195e7f5a3 for .NET
  Determining projects to restore...
  All projects are up-to-date for restore.
  hello-containers -> /workspaces/dotnet-containers/hello-containers/bin/Release/net8.0/hello-containers.dll
  hello-containers -> /workspaces/dotnet-containers/hello-containers/bin/Release/net8.0/publish/
  Building image 'hello-containers-alpine' with tags 'latest' on top of base image 'mcr.microsoft.com/dotnet/runtime:8.0-alpine'.
  Pushed image 'hello-containers-alpine:latest' to local registry via 'docker'.
```

Notice how the base image was changed from `mcr.microsoft.com/dotnet/runtime:8.0` to `mcr.microsoft.com/dotnet/runtime:8.0-alpine`. This is a smaller base image, which results in a smaller final image. Let's take a look at the size difference between the two images.

```bash
$ docker images
REPOSITORY                TAG       IMAGE ID       CREATED          SIZE
hello-containers-alpine   latest    60a63389d474   18 seconds ago   82.7MB
hello-containers          latest    ae96d4d7ac36   23 seconds ago   193MB
```

Less than half the size! That's a pretty big difference. Let's take a look at Ubuntu Chiseled, which just went GA.
 
## Ubuntu Chiseled

Ubuntu Chiseled is a lightweight version of Ubuntu, which is a popular linux distribution. Let's take a look at how we can use Ubuntu Chiseled to make our images smaller.

```bash
$ dotnet publish -t:PublishContainer -p:ContainerFamily=jammy-chiseled /p:ContainerRepository=hello-containers-chiseled
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

### **Why Choose Ubuntu Chiseled Images?**
- Smaller image size for quicker deployment.
- Enhanced security with minimized attack surface.

![.NET]({{ site.url }}{{ site.baseurl }}/assets/images/ubuntu-chiseled.png)

## **Exploring Alpine Images**

Alpine images offer a lightweight alternative, perfectly suited for .NET apps. We discuss how to publish for Alpine, focusing on its compatibility (glibc vs musl libc) and how it fits into various support contracts and lifecycles.

### **Benefits of Alpine Images**
- Small and efficient, optimizing resource usage.
- Compliance-friendly with minimal dependencies.

## **Streamlining with Project File Properties**

By moving publish properties to the project file, you enhance the compliance and security of your deployment process, making it less prone to errors and easier to audit.

## **Conclusion**

Publishing .NET console apps as OCI images provides a multitude of options to suit diverse needs. From targeting specific Linux distributions like Ubuntu or Alpine to choosing between framework-dependent or self-contained deployments, each method brings its unique benefits in terms of size, security, compliance, composability, compatibility, and support. This approach signifies a move towards more specialized and purpose-built container images, shaping the future of cloud applications.

## **Further Reading**

For those interested in diving deeper, we recommend exploring the following resources:
- [Official .NET Documentation](https://docs.microsoft.com/en-us/dotnet/)
- [Containerization and Docker Guides](https://www.docker.com/resources/what-container)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)

Thank you for joining us on this exploration of .NET and containers. Stay tuned for more insights and guides in our container workshop series!
