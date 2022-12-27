---
title: Multiple Domains on GitHub Pages
type: post
categories:
- Development
tags:
- GitHub
- dns
- cloudflare
- tools
mermaid: true
permalink: /2022/12/23/multiple-domains-on-github-pages
---

Something I found out after moving from Wordpress to GitHub Pages is that out of the box you can only host a single domain for a repo with GitHub Pages. This means for example, I can setup www.chris-ayers.com and chris-ayers.com for my repo and nothing else.
If I want another domain to point to it, I would need to fork the repo and setup the new repo for the additional domain.

I found a few articles that talk about how to do this, but they all seem to use different techniques. I wanted to write this post to document how I got it working for me.

## Official Docs and the limitation

So officially, GitHub pages doesn't support multiple domains. The docs say:
https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages

- blogs on it
https://medium.com/@desfocado/how-to-get-multiple-domains-pointing-to-github-pages-using-cloudflare-41fcb20ed10

https://olney.ai/category/2018/07/30/ai.html

https://deanattali.com/blog/multiple-github-pages-domains/

