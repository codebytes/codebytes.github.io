---
title: 'ARM - Part 1: Azure Resource Manager'
date: 2019-05-11 23:53:57.000000000 +00:00
type: post
categories:
- DevOps
tags:
- arm
- arm templates
- azure
- cli
- infrastructure
- Microsoft
- PowerShell
- scripts
permalink: "/2019/05/11/arm-azure-resource-manager/"
header:
  teaser: /assets/images/arm-logo.png
  og_image: /assets/images/arm-logo.png
---
### The Journey Begins

I've been an azure developer for years. Originally I worked with "Classic Mode" and Cloud Services. Then I moved to ARM and Web Apps. Lately I've been doing DevOps but I only recently started working with ARM Termplates. First, let's dive into a little history.

### History

Azure has grown and changed since it was first introduced. Originally, it was a research project called, "Project Red Dog". Azure has been commercially available since 2010. For four years, there was a limited way to interact with Azure, ASM the Azure Service Manager.

#### The Old Thing (Classic Mode) - ASM Azure Service Manager

The big problem with ASM was that all the resources were disconnected and separate. If you had multiple things you were creating, you had to keep track of them, create them in the right order, and make sure you deleted them all when things were removed. You were also limited in capabilities, like policies, tagging, and security. I remember the deployment scripts that you would write to check if things existed, poll when they got created, and you would have to keep tweaking to get it to run properly. Powershell was the language and script of choice.

#### The New Thing - ARM Azure Resource Manager

ARM was released in 2014. ARM is a great change. Instead of writing scripts to poll and make sure things were created, you can deploy and manage resources as a group. It opens the door for repeated deployments and templates. It lets you define the deployment order and apply tags and policies. You can still write Powershell, the but there are new modules for ARM (Azure-RM\*). But you can also use Azure CLI, Rest APIs and client SDKs. I will definitely be diving into the Azure CLI in the future. Right now, the part I'm loving, is that I can define my infrastructure as code.

#### ARM Templates

ARM Templates are amazing. I plan on diving deep into this over the next few blog posts. But what is awesome is that I can have my project source code and the infrastructure it runs on checked into the same repository. Those files can then be built and deployed together. I can continuously deploy my environment and the deployment can apply the differences as needed. Microsoft has some great documentation on [ARM Templates](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-authoring-templates). They also have a great quickstart resource: [Azure Quickstart Template](https://azure.microsoft.com/en-us/resources/templates/). I'll be diving into those topics next time in [part 2](https://chris-ayers.com/2019/05/13/arm-part-2-azure-quickstart-templates/).
