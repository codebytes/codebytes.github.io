---
title: Unleash Your Creativity with Marp Presentation Customization
type: post
categories:
  - Tools
tags:
  - vscode
  - marp
  - markdown
  - mermaid
mermaid: true
permalink: /2023/03/31/customizing-marp
header:
  teaser: /assets/images/marp-bg-full.png
  og_image: /assets/images/marp-bg-full.png
excerpt_separator: <!--more-->
---

This is part 2 of the [MARP](https://github.com/marp-team/marp) series. You can read the series of articles here:

- [Marp - Create Presentations with Markdown](/2023/03/26/marp-create-presentations-with-markdown)
- [Unleash Your Creativity with Marp Presentation Customization](/2023/03/31/customizing-marp)

## Introduction

Marp is a powerful Markdown presentation framework that enables you to create stunning slides effortlessly. By using simple text-based formatting, you can easily customize your presentations to suit your unique needs and style. Although Marp provides built-in themes and configurations, the true potential of this framework can be realized by customizing your presentations to suit your unique needs and style. In this blog post, we will delve into some of the key customization options available in Marp and guide you through the process of creating a truly standout presentation.

## Built-in Themes

Marp comes with [three built-in themes](https://github.com/marp-team/marp-core/tree/main/themes) that you can use to get started. The three themes, Default, Gaia, and Uncover, are shown below along with the frontmatter to use them and a few inverted examples.

### Default Theme

#### Default - Normal

```yaml
---
marp: true
theme: default
---
```

{% include figure image_path="/assets/images/marp-default.png" alt="Marp default theme" caption="Marp default theme" %}

#### Default - Inverted

```yaml
---
marp: true
theme: default
class:
  - invert
---
```

{% include figure image_path="/assets/images/marp-default-invert.png" alt="Marp default theme - Invert" caption="Marp default theme - Invert" %}

### Gaia Theme

#### Gaia Normal

```yaml
---
marp: true
theme: gaia
---
```

{% include figure image_path="/assets/images/marp-gaia.png" alt="Marp gaia theme" caption="Marp gaia theme" %}

#### Gaia - Lead / Invert

```yaml
---
marp: true
theme: gaia
class:
  - invert
  - lead
---
```

{% include figure image_path="/assets/images/marp-gaia-lead-invert.png" alt="Marp gaia theme - Lead/Invert" caption="Marp gaia theme - Lead/Invert" %}

### Uncover

#### Uncover Normal

```yaml
---
marp: true
theme: uncover
---
```

{% include figure image_path="/assets/images/marp-uncover.png" alt="Marp uncover theme" caption="Marp uncover theme" %}

## Directives

Directives are commands that you can use to customize your slides. They allow you to control the appearance, layout, and behavior of your presentation. Many of the directives apply globally to the entire presentation, but some are local and only apply to the current slide. A few of the directives include:

- fit
- backgroundColor
- color
- header
- footer
- class
- paginate
- many more...

To learn more about the directives and see more examples, check out the [Marp documentation](https://marpit.marp.app/directives).

## Custom Themes

Marp's built-in themes serve as an excellent starting point. In the marp-slides-template repository, we demonstrate how you can extend a theme. Let's take a look at the CSS file, `custom-default.css`:

```css
/* custom-default.css */
/* @theme custom-default */

@import 'default';

section {
  /* Override default background */
  background: #fff;
}
```

The crucial aspect for the Marp theme engine is the theme directive: `@theme custom-default`. This theme name is what you'll use in your slides. To link it to your Markdown file, apply the theme option in the front matter:

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

{% include figure image_path="/assets/images/marp-bg-full.png" alt="Marp full background" caption="Marp full background" %}

You can also use keywords to control how the background shows up. For instance, you can you left or right:

```markdown
![bg right](path/to/your/background-image.jpg)
```

{% include figure image_path="/assets/images/marp-bg-right.png" alt="Marp right background" caption="Marp right background" %}

or

```markdown
![bg left](path/to/your/background-image.jpg)
```

{% include figure image_path="/assets/images/marp-bg-left.png" alt="Marp left background" caption="Marp left background" %}

Another option is to specify a percentage, like if you wanted the image to only take up a smaller percentage.

```markdown
![bg left:35%](path/to/your/background-image.jpg)
```

{% include figure image_path="/assets/images/marp-bg-left-35.png" alt="Marp left background - 35%" caption="Marp left background - 35%" %}

There are also a bunch of filters that you can apply to your images to get various styles, like grayscale, sepia, blur, and opacity.

{% include figure image_path="/assets/images/marp-bg-right-grayscale.png" alt="Marp right background grayscale" caption="Marp right background grayscale" %}
{% include figure image_path="/assets/images/marp-bg-right-sepia.png" alt="Marp right background sepia" caption="Marp right background sepia" %}
{% include figure image_path="/assets/images/marp-bg-right-blur.png" alt="Marp right background blur" caption="Marp right background blur" %}
{% include figure image_path="/assets/images/marp-bg-right-opacity.png" alt="Marp right background opacity" caption="Marp right background opacity" %}

These filters apply to not only backgrounds, but regular images. You can also combine them.

{% include figure image_path="/assets/images/marp-image-filters.png" alt="Marp image multiple filters" caption="Marp image multiple filters" %}

You can also add background colors and gradients using CSS.

## Inline CSS

Another thing I've done is add inline CSS to my slides. I've also enabled HTML tags in my slides, so I can use divs and classes besides the standard Markdown syntax. To do this, you can use the following syntax in your frontmatter.

```css
---
marp: true
theme: default
style: |
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
---
```

We can then use these classes in our slides and mix and match Markdown and HTML if needed.

```markdown
---

![bg opacity](https://picsum.photos/800/600?image=53)

## Slide 5

<div class="columns">
<div>

## Left

- 1
- 2

</div>
<div>

## Right

- 3
- 4

</div>
</div>
```

In this example, I'm adding a grid layout to my slides so I have have split columns. You can add any CSS you want here.

{% include figure image_path="/assets/images/marp-html-css.png" alt="Marp HTML and custom CSS" caption="Marp HTML and custom CSS" %}

## Font Awesome

[Font Awesome](https://fontawesome.com/) is a great resource for designers, developers, and content creators who want to add visual elements to their projects without having to create them from scratch. Font Awesome provides a library of over [2,000 free icons](https://fontawesome.com/search?o=r&m=free) that you can use to enhance your presentations.

{% include figure image_path="/assets/images/marp-fa-icons.png" alt="Marp Font Awesome icons" caption="Marp Font Awesome icons" %}

To do this, you can use the following syntax in your frontmatter to import and style icons.

```css
---
marp: true
theme: default
style: |
  .fa-twitter { color: aqua; }
  .fa-mastodon { color: purple; }
  .fa-linkedin { color: blue; }
  .fa-window-maximize { color: skyblue; }
  @import 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css'
---
```

And then in your slides, you can use the following syntax to add icons.

```markdown
## Slide 6

<i class="fa-brands fa-twitter"></i> Twitter:
<i class="fa-brands fa-mastodon"></i> Mastodon:
<i class="fa-brands fa-linkedin"></i> LinkedIn:
<i class="fa fa-window-maximize"></i> Blog:
<i class="fa-brands fa-github"></i> GitHub:
```

## Mermaid Support

Marp also supports [Mermaid](https://mermaid-js.github.io/mermaid/#/), a JavaScript library for generating diagrams and flowcharts from text. Mermaid provides an easy way to create visual representations of complex ideas and concepts, and it integrates seamlessly with Markdown syntax.

To use Mermaid diagrams in your Marp presentation, you need to add the following script to your Markdown file:

```markdown
<!-- Add this anywhere in your Markdown file -->
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
```

You can then create Mermaid diagrams using the div element with the mermaid class. For example:

```md
# Mermaid

<div class="mermaid">
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
</div>
```

{% include figure image_path="/assets/images/marp-mermaid.png" alt="Marp mermaid diagrams" caption="Marp mermaid diagrams" %}

Marp will automatically convert this code into a diagram, which you can then style using CSS. By default, Mermaid diagrams are quite small, but you can adjust their size using CSS. This CSS code will make your Mermaid diagrams larger and easier to read. You can add this code to the frontmatter section of your Markdown file.

```css
svg[id^='mermaid-'] {
  min-width: 480px;
  max-width: 960px;
  min-height: 360px;
  max-height: 600px;
}
```

And we get the following:

{% include figure image_path="/assets/images/marp-mermaid-styled.png" alt="Marp mermaid diagrams - with CSS" caption="Marp mermaid diagrams - with CSS" %}

Note that out of the box, VS Code doesn't support Mermaid diagrams with a preview, but you can add this feature using the [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) extension. This extension adds support for Mermaid diagrams in the preview pane of VS Code.

## Speaker Mode

Marp comes with a built-in speaker mode that allows presenters to view their notes and upcoming slides while giving a presentation. To enable speaker mode:

- Export your presentation to HTML (you can also use my template and leverage GitHub Pages).
- Open your Marp presentation file in your browser.
- Press "P" on your keyboard or click on the icon for speaker mode.

{% include figure image_path="/assets/images/marp-speaker.png" alt="Marp Speaker options" caption="Marp Speaker options" %}

- A new window will open, displaying the current slide, next slide, and speaker notes.

{% include figure image_path="/assets/images/marp-speaker-mode.png" alt="Marp Speaker mode" caption="Marp Speaker mode" %}

### Adding Speaker Notes

To add speaker notes to your Marp slides, use the following syntax:

```markdown
---
<!-- Your speaker notes go here. -->

<!--
Or Your speaker
notes go here.
-->
---
```

This will create a hidden area for your speaker notes, which will be visible only in speaker mode. You can also export them to PowerPoints and PDF.

## Conclusion

In conclusion, Marp is a powerful and flexible presentation tool that can help you create stunning slides with ease. Unlike traditional presentation tools like PowerPoint, Marp uses Markdown, a lightweight markup language that allows you to focus on your content without getting bogged down in formatting details. With Marp, you can easily customize your presentations with custom themes, images, CSS, and other features, making your slides truly stand out. Additionally, Marp is free and open-source, so you don't have to worry about licensing fees or vendor lock-in. Overall, Marp is a fantastic alternative to traditional presentation tools, and we encourage you to give it a try!

Get started today by using the [Marp Slides Template](https://github.com/codebytes/marp-slides-template) to create your own Marp presentation!

## References

- [Marp Slides Template](https://github.com/codebytes/marp-slides-template)
- [Marp Site](https://marp.app/)
- [Marp Documentation](https://marpit.marp.app/)
- [Font Awesome](https://fontawesome.com/)
- [Mermaid Documentation](https://mermaid-js.github.io/mermaid/#/)
- [Markdown Preview Mermaid Support Extension](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)
