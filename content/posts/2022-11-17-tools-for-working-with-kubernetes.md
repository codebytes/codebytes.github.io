---
title: Tools for working with Kubernetes
date: '2022-11-17'
categories:
- Tools
tags:
- Kubernetes
- tools
image: images/kubernetes-logo.png
featureImage: images/kubernetes-logo.png
aliases:
- /2022/11/17/tools-for-working-with-kubernetes/
- /tools/tools-for-working-with-kubernetes/
slug: tools-for-working-with-kubernetes
---
I've been in a number of internal and external calls where tooling to help work with Kubernetes keeps coming up. I thought I would share some of these cool tools in case you weren't aware of them.

## Tools

- K9S
- kubectx and kubens
- fzf

### K9S

K9S is a terminal based UI for interacting and managing Kubernetes Clusters. You can find k9s at [https://github.com/derailed/k9s](https://github.com/derailed/k9s) or their site [https://k9scli.io/](https://k9scli.io/).

{{< figure src="/images/k9s-main.png" alt="k9s main screen" >}}

### Kubectx and Kubens

These tools are amazing at quickly switching context and namespaces while working with kubernetes.
You can find k9s at [https://github.com/ahmetb/kubectx](https://github.com/ahmetb/kubectx) or the author's site [https://ahmet.im/blog/kubectx/](https://ahmet.im/blog/kubectx/).

kubectx can show you the multiple contexts available, switch between them quickly, and create aliases.

{{< figure src="/images/kubectx-demo.gif" >}}

kubens can show you the multiple namespaces available, switch between them quickly, and create aliases.

{{< figure src="/images/kubens-demo.gif" >}}

### fzf

fzf is a different type of tool. This makes your other tools better. It works on a variety of platforms but what is allows you to do is get an interactive filter. kubectx and kubens will show the list and let you pick what you want instead of runnig multiple commands.
You can leverage fzf to pick files to edit more quickly.

{{< figure src="/images/fzf.gif" >}}

It works with lots of things, like vi.

{{< figure src="/images/fzf-vi.gif" >}}

## Conclusion

If you work daily with Kubernetes you might already know about these tools. If you haven't tried them, give them an install and play around.

## GitHub Repositories

{{< github repo="derailed/k9s" >}}
{{< github repo="ahmetb/kubectx" >}}
