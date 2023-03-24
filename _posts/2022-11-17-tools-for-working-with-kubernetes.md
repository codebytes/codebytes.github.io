---
title: Tools for working with Kubernetes
type: post
categories:
- Tools
tags:
- kubernetes
- tools
header:
  image: /assets/images/kubernetes-logo.png
permalink: /2022/11/17/tools-for-working-with-kubernetes/
k9s-gallery:
- url: /assets/images/k9s-pulses.png
  image_path: /assets/images/k9s-pulses.png
  alt: k9s pulses
  title: k9s pulses
- url: /assets/images/k9s-logs.png
  image_path: /assets/images/k9s-logs.png
  alt: k9s logs
  title: k9s logs
- url: /assets/images/k9s-pods.png
  image_path: /assets/images/k9s-pods.png
  alt: k9s pods
  title: k9s pods
- url: /assets/images/k9s-rbac.png
  image_path: /assets/images/k9s-rbac.png
  alt: k9s rbac
  title: k9s rbac
---

I've been in a number of internal and external calls where tooling to help work with Kubernetes keeps coming up. I thought I would share some of these cool tools in case you weren't aware of them. 

## Tools

- K9S
- kubectx and kubens
- fzf

### K9S

K9S is a terminal based UI for interacting and managing Kubernetes Clusters. You can find k9s at [https://github.com/derailed/k9s](https://github.com/derailed/k9s) or their website [https://k9scli.io/](https://k9scli.io/).


{% include gallery id="k9s-gallery" caption="k9s Screens" %}

### Kubectx and Kubens

These tools are amazing at quickly switching context and namespaces while working with kubernetes.
You can find k9s at [https://github.com/ahmetb/kubectx](https://github.com/ahmetb/kubectx) or the author's website [https://ahmet.im/blog/kubectx/](https://ahmet.im/blog/kubectx/).

kubectx can show you the multiple contexts available, switch between them quickly, and create aliases.

{% include figure image_path="/assets/images/kubectx-demo.gif" alt="kubectx" caption="kubectx" %}

kubens can show you the multiple namespaces available, switch between them quickly, and create aliases.

{% include figure image_path="/assets/images/kubens-demo.gif" alt="kubens" caption="kubens" %}

### fzf

fzf is a different type of tool. This makes your other tools better. It works on a variety of platforms but what is allows you to do is get an interactive filter.  kubectx and kubens will show the list and let you pick what you want instead of runnig multiple commands.
You can leverage fzf to pick files to edit more quickly.

{% include figure image_path="/assets/images/fzf.gif" alt="fzf" caption="fzf" %}

It works with lots of things, like vi.

{% include figure image_path="/assets/images/fzf-vi.gif" alt="fzf-vi" caption="fzf-vi" %}

## Conclusion

If you work daily with Kubernetes you might already know about these tools. If you haven't tried them, give them an install and play around. 