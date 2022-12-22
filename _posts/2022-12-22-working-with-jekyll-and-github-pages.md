---
title: Working with Jekyll and GitHub Pages
type: post
categories:
- Development
tags:
- jekyll
- GitHub
- markdown
- ruby
mermaid: true
permalink: /2022/12/22/working-with-jekyll-and-github-pages
---

I haven't done a lot with jekyll in the past, but I'm a big fan of MarkDown everything. For me that usually means I'm taking notes in markdown [Obsidian](https://obsidian.md]), doing diagrams in mermaid in Azure DevOps or [https://mermaid.live/](https://mermaid.live/). I've even started turning my talk slides into MarkDown with a tool called [MARP](https://marp.app/).

Understanding when I use standard MarkDown or some sort of templating language (jekyll uses Liquid) has been fun.  I'll do something in html or MarkDown, then find out that Jekyll or my theme already has helpers to render that (like gists, videos, and figures). Sometimes rendering more advanced things takes a little tweaking of Jekyll and the theme.

Lets take Mermaid for example.  If I want to render mermaid, I actually need to inialize things manually.

If I want to render a graph, this won't work out of the box. 
```
    '''mermaid
    graph TD;
        A-->B;
        A-->C;
        B-->D;
        C-->D;
    '''
```

So to make it work, i looked at the themes layouts.  They live in the _layout folder [here](https://github.com/mmistakes/minimal-mistakes/tree/master/_layouts). These are the base structure of a page and most reference either Archive or Default. Fortunately Archive also refers to Default so I can focus my changes there if I want to override it.  Overriding a theme in Jekyll seems easy enough. I'm using a Gem theme, so it just works but if I add a file named the same as the theme file, my file overrides it.

{% include figure image_path="/assets/2022/12/minimal-mistakes-layout-posts.png" alt="" caption="" %}

{% include figure image_path="/assets/2022/12/minimal-mistakes-layout-archive.png" alt="" caption="" %}

{% include figure image_path="/assets/2022/12/minimal-mistakes-layout-default.png" alt="" caption="" %}

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```
