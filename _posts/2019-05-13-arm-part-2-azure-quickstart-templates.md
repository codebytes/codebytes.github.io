---
#layout: post
title: 'ARM - Part 2: Azure Quickstart Templates'
date: 2019-05-13 20:59:03.000000000 +00:00
type: post
categories:
- DevOps
tags:
- arm
- arm templates
- azure
- functions
- json
permalink: "/2019/05/13/arm-part-2-azure-quickstart-templates/"
header:
  teaser: /assets/images/arm-logo.png
  og_image: /assets/images/arm-logo.png
---
## Time to Dive in

I'm one of those guys that likes to learn by doing. Reading the documentation is great, and I do that a lot. But for me to really _grok_ something, I need to play with it, run it, and probably blow it up.

If you missed [part 1](http://chris-ayers.com/arm-azure-resource-manager), read along and come back. I need a WebApp setup for my sample project. I realized I can do it a few ways. Some of the ways are very manual, some are repeatable, but one stood out to me.

- Create the resources in the Azure Portal
- Create the resources in Visual Studio when I right-click Publish
- Create the resources via a Powershell script
- Create the resources via the Azure CLI
- **Create an ARM Template, create the resources on deploy, or via the CLI**

## Let's Write an ARM Template

I know what I want to do, write an ARM Template. Do I have any idea what I'm doing or where to start at this point? **No.** Fortunately for me, Microsoft provides a **BUNCH** of resources to get you started. There is an [entire searchable quickstart page](https://azure.microsoft.com/en-us/resources/templates/) with examples (backed by a [github repo](https://www.github.com/Azure/azure-quickstart-templates)) as well the [Microsoft Docs on ARM Templates](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-authoring-templates).

Well, I found one in the quickstart: [https://learn.microsoft.com/en-us/azure/app-service/quickstart-arm-template?pivots=platform-windows](https://learn.microsoft.com/en-us/azure/app-service/quickstart-arm-template?pivots=platform-windows). From this quickstart, I can click Deploy to Azure, fill out some information and I've got an App Service Plan and a Web App. **This is so cool.** Now to tear this thing apart and figure out what it is.

## Ok, Lets play with an ARM Template

In the [github repo](https://github.com/Azure/azure-quickstart-templates/tree/master/quickstarts/microsoft.web/webapp-basic-windows) it looks like there are 2 or 3 files that make up the ARM Template.

### Dissection

Lets dissect [azuredeploy.json](https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.web/webapp-basic-windows/azuredeploy.json). Schema, version, blah...

#### Parameters

My eye is drawn to the Parameters section. I recognize some of these from when I deployed to Azure. Getting a feel for parameters I see you can have metadata describing them, types, lengths, and default values. This gives me lots of ideas and options.

#### Variables

This isn't your mama's json. That looks like a function to me! Looks like somebody got their code in my json. I like it. A quick google later and I see a huge list of [template functions](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-template-functions) in Microsoft's documentation. I'll come back to that. In the mean time, those variables look a lot like the name of the webapp and AppServicePlan. I can work with this.

#### Resources

Meat and potatoes. Jackpot. This looks like where the resources are defined. Only a few properties on each, an apiVer, type, name, location, sku, and a few others. I also notice one has a "dependsOn" property, I bet I can build up what depends on what and it will do everything in the right order.

## Next Steps

I've got an ARM Template now that works. I've poked at it a little. Time to make this thing _fly_. Lets setup an Azure Repo on DevOps and see about trying to deploy this thing and create my webapp on release. I want to be able to check in a change and have it create/update my resources in azure. Next time, we start the feedback loop.
