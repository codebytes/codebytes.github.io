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
---
Containers are a very big topic right now, but they also cause a lot of confusion for people. Before we discuss containers, containerization, and container orchestration; we should address the question of how containers differ from virtual machines (VMs).

Both are built on the concept of Virtualization. Virtualization is the process of creating a virtual computing environment as opposed to a physical environment. Both technologies have their uses, and even today many solutions leverage both VMs and containers, sometimes leveraging VMs to host containers.

## What are VMs?

A virtual machine (VM) is virtual infrastructure with its own virtual CPU, memory, network interface (NIC), and storage. A host machine runs VMs. The VMs that run on the host are called guests. The resources of the host are managed by a hypervisor.

The hypervisor is software that creates and runs VMs. The hypervisor gives each virtual machine the resources that have been allocated and manages the scheduling of VM resources against the physical resources. VMs are isolated from the rest of the system, and multiple VMs can exist on a single host. Because they are isolated, VMs can run different operating systems like Linux or Windows.

Workloads or applications running on a VM contain the entire operating system (Linux, Windows, ...) as well as all the services, dependencies, and libraries needed to run and administer applications or workloads. Because VM images contain the entire operating system, they can range in size from hundred of megabytes up to several gigabytes. Starting a VM or application can also take several seconds to minutes

{% include figure image_path="/assets/images/containers-vms.png" alt="VMs" caption="VMs" %}

#### Pros

*   VMs offer the ability to run multiple applications requiring different OSs on a single piece of infrastructure
*   VMs emulate an entire computing environment: cpu, memory, storage, networking
*   VMs simplify the portability and migration between on-premises and cloud-based platforms
*   VMs can provide more isolation and security between systems
*   There is a vast, established VM ecosystem and marketplace with industry leaders such as VMware, Microsoft Hyper-V, Nutanix, Linux KVM, Azure, AWS, Google, Oracle and many more.

#### Cons

*   VM images typically consume gigabytes and thus take longer to backup or migrate between platforms
*   Multiple VMs in a system can have many duplicate copies of the same files (OS or Libraries)
*   Because they encapsulate the entire server including OS, a physical server can support fewer VMs than containers
*   VM start-up time can take minutes because the entire OS and kernel need to start up.

## What are Containers?

Containers are lightweight, isolated, packages of software. The containers bundle libraries, configuration, scripts, and application binaries. There is a standard for containers images, The Open Container Initiative - OCI, for allowing interoperability of different container engines. Containers run on top of an OS and a Container Engine, like Docker, CRI-O, or LXD. The Container Engine pulls images from a container registry and runs applications.

{% include figure image_path="/assets/images/containers-containers.png" alt="Containers" caption="Containers" %}

#### Pros

*   Containers are more lightweight than VMs, as their images are measured in megabytes rather than gigabytes
*   Containers are extremely portable, able to run on prem, public cloud, hybrid cloud, or private cloud.
*   Containers require fewer IT resources to deploy, run, and manage
*   Containers spin up in seconds
*   A single system can host many more containers as compared to VMs

#### Cons

*   Containers have a steeper learning curve
*   All containers must run atop the same OS, you can't mix and match OSs or versions (Windows, Linux, Unix)
*   Containers may be less secure than VMs since the underlying OS is shared
*   Containers are a newer technology, and the ecosystem is still evolving

## Next Steps

While VMs emulate entire machines, Containers are great for packaging applications and their dependencies. Next time we'll look at the parts of a container image, how they are defined, and how they are run.
