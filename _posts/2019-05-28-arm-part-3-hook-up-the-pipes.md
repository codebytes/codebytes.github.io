---
#layout: post
title: 'ARM - Part 3: Hook up the Pipes'
date: 2019-05-28 18:30:31.000000000 +00:00
type: post
categories:
  - DevOps
tags:
  - arm
  - arm templates
  - azure
  - git
permalink: '/2019/05/28/arm-part-3-hook-up-the-pipes/'
header:
  teaser: /assets/images/arm-logo.png
  og_image: /assets/images/arm-logo.png
---

I’ve got a template straight from Microsoft. I want this wired into a CI/CD pipeline to I can play around and get quick feedback. I’m going to use Azure DevOps to help make all this possible. Let's get those templates into a repository to get started. New repository, initialize it, add new files.

{% include figure image_path="/assets/images/repoimport.png" alt="A new repository on Azure DevOps" caption="A new repository on Azure DevOps." %}

Next, I'm going to create a new resource group to play around with my web app resources.

{% include figure image_path="/assets/images/newresourcegroup-3.png" alt="A new Azure Resource Group." caption="A new Azure Resource Group." %}

Now we need to make sure DevOps has permission to create and update resources in Azure. This can be done in a few different ways as described here: [https://docs.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops).

I'm going to setup a service connection from DevOps to Azure. In Azure Devops, I'm going to go to my project settings:

{% include figure image_path="/assets/images/projectsettings.png" alt="Azure DevOps Project Settings" caption="Azure DevOps Project Settings" %}

And go to Service Connections:

{% include figure image_path="/assets/images/serviceconnections.png" alt="Create a Service Connection" caption="Create a Service Connection" %}

We'll create a new Azure Resource Manager service connection.

{% include figure image_path="/assets/images/serviceconnectionarm.png" alt="Create a Service Connection for ARM" caption="Create a Service Connection for ARM" %}

We just need to pick the right Subscription, Sign in, and point it at our resource group. There are more complex setups, and we'll get into those in the future, but for now we'll just point it at that resource group I created earlier. Now for this to work properly, you have to be able to grant rights to the connector.

{% include figure image_path="/assets/images/serviceconnectionarm2-4.png" alt="Create a Service Connection for ARM" caption="Create a Service Connection for ARM" %}

Now we've got a connector to deploy to Azure. We'll finish this up next time.
