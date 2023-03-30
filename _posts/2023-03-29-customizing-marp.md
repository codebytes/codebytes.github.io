---
title: Unleash Your Creativity with Marp Presentation Customization
type: post
categories:
- Development
tags:
- tools
- github
- markdown
mermaid: true
permalink: /2023/03/29/customizing-marp
header:
  teaser: /assets/images/marp-logo.png
  og_image: /assets/images/marp-logo.png
excerpt_separator: <!--more-->
---

# Unleash Your Creativity with Marp Presentation Customization

## Introduction

Marp is a powerful Markdown presentation framework that enables you to create stunning slides effortlessly. Although Marp provides built-in themes and configurations, the true potential of this framework can be realized by customizing your presentations to suit your unique needs and style. In this blog post, we will delve into some of the key customization options available in Marp and guide you through the process of creating a truly standout presentation.

## Custom Themes

Marp's built-in themes serve as an excellent starting point. In the marp-slides-template repo, we demonstrate how you can extend a theme. Let's take a look at the CSS file, `custom-default.css`:

```css
/* custom-default.css */
/* @theme custom-default */

@import 'default';

section {
  /* Override default background */
  background: #fff;
}
```

The crucial aspect for the Marp theme engine is the theme directive: /* @theme custom-default */. This theme name is what you'll use in your slides. To link it to your Markdown file, apply the theme option in the front matter:

```markdown
---
marp: true
theme: custom-default
---
```

In your CSS file, override or extend Marp's default styles to craft your unique appearance. For instance, you can modify the background color, font, or slide transitions. For a comprehensive list of available style properties, refer to the Marp documentation: [https://marpit.marp.app/theme-css](https://marpit.marp.app/theme-css).

## Backgrounds and Images

### Backgrounds

Adding custom backgrounds and images can make your presentation more engaging and visually appealing. To add a background image to a specific slide, use the following syntax:

```markdown
![bg](path/to/your/background-image.jpg)
```

![](/assets/images/marp-bg-full.png)

You can also use keywords to control how the background shows up. For instance, you can you left or right:

```markdown
![bg right](path/to/your/background-image.jpg)
```

![](/assets/images/marp-bg-right.png)

or

```markdown
![bg left](path/to/your/background-image.jpg)
```

![](/assets/images/marp-bg-left.png)

Another option is to specify a percentage, like if you wanted the image to only take up a smaller percentage.

```markdown
![bg left:35%](path/to/your/background-image.jpg)
```

![](/assets/images/marp-bg-left-35.png)

There are also a bunch of filters that you can apply to your images to get various styles, like grayscale, sepia, blur, and opacity.


You can also add background colors and gradients using CSS.


## Conclusion

Marp is a versatile tool for creating visually stunning presentations with Markdown. By exploring and experimenting with its customization options, you can design a presentation that perfectly reflects your personal style and content. So go ahead, unleash your creativity and make your Marp presentations truly unforgettable!

Happy presenting!
