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
permalink: "/2019/05/28/arm-part-3-hook-up-the-pipes/"
---
I’ve got a template straight from Microsoft. I want this wired into a CI/CD pipeline to I can play around and get quick feedback. I’m going to use Azure DevOps to help make all this possible. Let's get those templates into a repo to get started. New repo, initialize it, add new files.

![]({{ site.baseurl }}/assets/2019/05/repoimport.png)

Next, I'm going to create a new resource group to play around with my web app resources.

![]({{ site.baseurl }}/assets/2019/05/newresourcegroup-3.png)

Now we need to make sure DevOps has permission to create and update resources in Azure. This can be done in a few different ways as described here: https://docs.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops

I'm going to setup a service connection from DevOps to Azure. In Azure Devops, I'm going to go to my project settings:

![]({{ site.baseurl }}/assets/2019/05/projectsettings.png)

And go to Service Connections:

![]({{ site.baseurl }}/assets/2019/05/serviceconnections.png)

We'll create a new Azure Resource Manager service connection.

![]({{ site.baseurl }}/assets/2019/05/serviceconnectionarm.png)

We just need to pick the right Subscription, Sign in, and point it at our resource group. There are more complex setups, and we'll get into those in the future, but for now we'll just point it at that resource group I created earlier. Now for this to work properly, you have to be able to grant rights to the connector.

![]({{ site.baseurl }}/assets/2019/05/serviceconnectionarm2-4.png)

Now we've got a connector to deploy to Azure. We'll finish this up next time.