---
#layout: post
title: WSL2, Docker, and Time
date: 2020-01-23 11:42:30.000000000 +00:00
type: post
categories:
- Tools
tags:
- docker
- linux
- windows
- wsl
permalink: "/2020/01/23/wsl2-docker-and-time/"
---
I'm running on a Windows Insider Slow build so that I can leverage [WSL 2](https://docs.microsoft.com/en-us/windows/wsl/wsl2-index), the Windows Subsystem for Linux v 2. Its pretty incredible, because there's now a Linux kernel inside Windows. Ubuntu is fast, its a wonderful development experience all my favorite linux tools. I can't wait for this to be out of preview this year and in the mainstream windows releases.

I'm also using the latest version of Docker Desktop, with WSL2 support. What this means is that instead of using Hyper-V to run a Moby Linux VM, [docker runs directly on WSL2](https://docs.docker.com/docker-for-windows/wsl-tech-preview/). It also has built in Kubernetes support.

{% include figure image_path="/assets/2020/01/docker-logo.png" alt="Docker Logo" caption="Docker Logo" %}

If you haven't guessed, I've been doing some container development. The experience so far as been great, with [VS Code](https://code.visualstudio.com/) and the [Remote Development Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) pack. I recently ran into some issues though. Here are some examples from bug posts opened about it:

*   While updating Ubuntu: E: Release file for http://security.ubuntu.com/ubuntu/dists/bionic-security/InRelease is not valid yet (invalid for another 14h 47min 54s). Updates for this repository will not be applied.
*   Getting metadata from plugin failed with error: invalid_grant: Invalid JWT: Token must be a short-lived token (60 minutes) and in a reasonable timeframe. Check your iat and exp values and use a clock with skew to account for clock differences between systems.
*   kubectl x509 certificate has expired or is not yet valid #1152
*   Az storage blob copy start failed #9995

I tried resolving the issue by syncing my time clock and restarting but I kept having issues. I figured it out today. Turns out, WSL2 has a issue (being worked on) with skewed clocks. Even though my Windows time was correct, the time in my WSL was off. It was not syncing with local system time and was probably based on the first time I powered it up.

There are a few open issues on github regarding the problem, so I know they're aware and working on a fix.

*   Time not synced in WSL2 - causing TLS issues - [https://github.com/microsoft/WSL/issues/4149](https://github.com/microsoft/WSL/issues/4149)
*   system date is not same with windows (WSL 2) - [https://github.com/microsoft/WSL/issues/4245](https://github.com/microsoft/WSL/issues/4245)
*   WSL2: Clock skewed? - [https://github.com/microsoft/WSL/issues/4677](https://github.com/microsoft/WSL/issues/4677)

For me i first fixed the symtom, then followed the recommendation and actually solved the problem.  
Treating the symptom:

```bash
sudo ntpdate pool.ntp.org
```

But the actual recommendation from the team I used is:

```bash
sudo hwclock -s
```

I hope this helps someone until this goes GA. Thanks for your time!