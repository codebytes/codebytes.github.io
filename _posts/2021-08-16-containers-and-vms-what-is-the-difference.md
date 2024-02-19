---
#layout: post
title: 'Containers and VMs: What is the difference?'
date: 2021-08-16 12:01:41.000000000 +00:00
type: post
categories:
- Development
- DevOps
- Tools
tags:
- containers
- vms
permalink: "/2021/08/16/containers-and-vms-what-is-the-difference/"
header:
  teaser: /assets/images/containers-teaser.jpg
  og_image: /assets/images/containers-teaser.jpg

---
Containers are a very big topic right now, but they also cause a lot of confusion for people. Before we discuss containers, containerization, and container orchestration; we should address the question of how containers differ from virtual machines (VMs).

Both are built on the concept of Virtualization. Virtualization is the process of creating a virtual computing environment as opposed to a physical environment. Both technologies have their uses, and even today many solutions leverage both VMs and containers, sometimes leveraging VMs to host containers.

## What are VMs?

A virtual machine (VM) is virtual infrastructure with its own virtual CPU, memory, network interface (NIC), and storage. A host machine runs VMs. The VMs that run on the host are called guests. The resources of the host are managed by a hypervisor.

The hypervisor is software that creates and runs VMs. The hypervisor gives each virtual machine the resources that have been allocated and manages the scheduling of VM resources against the physical resources. VMs are isolated from the rest of the system, and multiple VMs can exist on a single host. Because they are isolated, VMs can run different operating systems like Linux or Windows.

Workloads or applications running on a VM contain the entire operating system (Linux, Windows, ...) as well as all the services, dependencies, and libraries needed to run and administer applications or workloads. Because VM images contain the entire operating system, they can range in size from hundred of megabytes up to several gigabytes. Starting a VM or application can also take several seconds to minutes

{% include figure image_path="/assets/images/containers-vms.png" alt="VMs" caption="VMs" %}

| Advantages | Disadvantages |
| --- | --- |
| VMs support diverse OS requirements for multiple applications on a single infrastructure | VM image size results in longer backup or migration durations between platforms |
| VMs replicate comprehensive computing environments, easing portability and migration between on-premises and cloud platforms | Duplicate copies of files (OS or libraries) are common among multiple VMs on a system |
| VMs provide superior isolation and security across systems | Limited VM support on a physical server compared to containers, due to full server encapsulation |
| A robust VM ecosystem and marketplace exists, featuring industry leaders | VM start-up times can be lengthy, as the OS and kernel need to fully initialize |

## What are Containers?

Containers are lightweight, isolated, packages of software. The containers bundle libraries, configuration, scripts, and application binaries. There is a standard for containers images, The Open Container Initiative - OCI, for allowing interoperability of different container engines. Containers run on top of an OS and a Container Engine, like Docker, CRI-O, or LXD. The Container Engine pulls images from a container registry and runs applications.

{% include figure image_path="/assets/images/containers-containers.png" alt="Containers" caption="Containers" %}

| Advantages | Disadvantages |
| --- | --- |
| Containers are lightweight with images in megabytes, compared to VMs in gigabytes | Steeper learning curve for containers |
| Containers offer high portability across on-premises and cloud environments | Containers require a uniform OS, limiting OS diversity or version mixing |
| Reduced IT resources needed for container deployment, operation, and management | Potential security concerns due to shared OS in containers compared to VMs |
| Rapid container start-up times in seconds | Containers are a newer technology with an evolving ecosystem |

## Next Steps

While VMs emulate entire machines, Containers are great for packaging applications and their dependencies. Next time we'll look at the parts of a container image, how they are defined, and how they are run.
