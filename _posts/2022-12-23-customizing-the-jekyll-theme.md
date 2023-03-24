---
title: Customizing the Jekyll Theme
type: post
categories:
- Development
tags:
- jekyll
- GitHub
- markdown
- ruby
- mermaid
- tools
mermaid: true
permalink: /2022/12/23/customizing-the-jekyll-theme
redirect_from:
  - /2022/12/23/customizing-my-chosen-jekyll-theme-minimal-mistakes

---

I haven't done a lot with jekyll in the past, but I'm a big fan of MarkDown everything. For me that usually means I'm taking notes in markdown [Obsidian](https://obsidian.md]), doing diagrams in mermaid in Azure DevOps or [https://mermaid.live/](https://mermaid.live/). I've even started turning my talk slides into MarkDown with a tool called [MARP](https://marp.app/).

Understanding when I use standard MarkDown or some sort of templating language (jekyll uses Liquid) has been fun. I'll do something in html or MarkDown, then find out that Jekyll or my theme already has helpers to render that (like gists, videos, and figures). Sometimes rendering more advanced things takes a little tweaking of Jekyll and the theme.

Lets take Mermaid for example.  If I want to render mermaid, it won't work out of the box with jekyll or my theme. I need to tweak things and inialize things manually. If I want to render a graph, this won't work out of the box. 

```
    '''mermaid
    graph TD;
        A-->B;
        A-->C;
        B-->D;
        C-->D;
    '''
```

So to make it work, I had to override the base theme. To start, I looked at the themes layouts. They live in the _layout folder of the theme [here](https://github.com/mmistakes/minimal-mistakes/tree/master/_layouts). These are the base structure of a page and most reference either Archive or Default. 

{% include figure image_path="/assets/images/minimal-mistakes-layout-posts.png" alt="Theme layout for posts" caption="Theme layout for posts" %}

{% include figure image_path="/assets/images/minimal-mistakes-layout-archive.png" alt="Theme layout for archive" caption="Theme layout for archive" %}

Fortunately Archive also refers to Default so I can focus my changes there if I want to override it. 

{% include figure image_path="/assets/images/minimal-mistakes-layout-default.png" alt="Theme layout for default" caption="Theme layout for default" %}

Looking at this file, there are a few includes defined. One of which is the footer/custom.html and one is scripts.html. I looked through the scripts.html and it has a lot of logic I'd prefer not to duplicate. I'm alreadying using the header-custom file to define some css/scripts. I've found Mermaid needs its init to run in the body, so i'll probably want to leverage the footer/custom.html for this. It's an empty file in the theme, making it any easy choice to override.

I created a footer folder in my local project _includes and a custom.html file. I added some simple logic to only add the mermaid logic if I added a ```mermaid:true``` flag at the top of the page.

{% include figure image_path="/assets/images/custom-footer.png" alt="Custom footer logic for mermaid" caption="Custom footer logic for mermaid" %}

So lets set that!

{% include figure image_path="/assets/images/mermaid-frontmatter.png" alt="Front Matter flag for mermaid" caption="Front Matter flag for mermaid" %}

At this point, everthing should work and embedded mermaid in my markdown posts renders properly!

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```

I've done a few other minor customizations so far. Like adding some custom css and some javascript for app insights. Both of those involved a similar process of adding head/custom.html and assets/css/custom.css. 

I used a few different sources to get things to work for me. Please check those out as well to see if they can help you:

- [https://it-journey.dev/docs/jekyll-diagram-with-mermaid](https://it-journey.dev/docs/jekyll-diagram-with-mermaid)
- [https://github.com/jasonbellamy/jekyll-mermaid](https://github.com/jasonbellamy/jekyll-mermaid)
- [https://jojozhuang.github.io/tutorial/jekyll-diagram-with-mermaid](https://jojozhuang.github.io/tutorial/jekyll-diagram-with-mermaid)
- [https://github.com/kitian616/jekyll-TeXt-theme/blob/master/_includes/markdown-enhancements/mermaid.html](https://github.com/kitian616/jekyll-TeXt-theme/blob/master/_includes/markdown-enhancements/mermaid.html)
- [https://stackoverflow.com/questions/53883747/how-to-make-github-pages-markdown-support-mermaid-diagram](https://stackoverflow.com/questions/53883747/how-to-make-github-pages-markdown-support-mermaid-diagram)
- [https://github.com/mtrienis/jekyll-mermaid-blog](https://github.com/mtrienis/jekyll-mermaid-blog)

Thanks for following along on this journey. I hope this helps those starting their Jekyll journey or hosting on GitHub Pages.
