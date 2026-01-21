---
title: "Migrating from Jekyll to Hugo Part 1: Why I Made the Switch"
date: 2026-01-20
draft: false
categories:
  - Blog
tags:
  - Hugo
  - Jekyll
  - GitHub Pages
  - Blowfish
  - Markdown
  - Ruby
  - Static Site Generator
description: "Why I moved this blog from Jekyll to Hugo and chose the Blowfish theme."
featureimage: "images/logos/hugo-logo.svg"
excerpt_separator: "<!--more-->"
---

{{< figure src="images/logos/hugo-logo.svg" alt="Hugo Logo" class="mx-auto" width="200" >}}

After years of running this blog on Jekyll, I finally made the switch to Hugo. Here's why.

<!--more-->

## Why I Made the Switch

Static site generators have evolved a lot since Jekyll first popularized the idea of building blogs from Markdown. Jekyll served me well for a long time, but as my site grew and my workflow matured, a few pain points became impossible to ignore:

- **Build times**: As my site grew, Jekyll builds slowed to a crawl. Waiting 30+ seconds for a rebuild made local development feel sluggish.
- **Ruby dependencies**: Managing Ruby versions, gems, and Bundler across machines and CI environments was a recurring frustration.
- **Theme flexibility**: I wanted a more modern design system, better dark mode support, and a theme ecosystem that felt alive.

Hugo promised faster builds, a single binary with no external dependencies, and a more modern templating system. Once I started experimenting, the difference was immediate.

## Why Hugo Is a Better Fit

### Fast builds

Hugo compiles entire sites in milliseconds, and the dev server hot reload feels instant. That alone dramatically improves the writing and editing experience.

### No dependency headaches

Hugo is just one binary. No Ruby, no Bundler, no gem conflicts, no version juggling. It works the same on every machine and every CI pipeline.

### A more powerful templating system

Hugo's Go-based templating is far more flexible than Liquid. It supports:

- Rich built-in functions
- Complex content structures
- Custom taxonomies
- Shortcodes
- Image processing
- Multilingual content

Many things that require plugins in Jekyll are built directly into Hugo.

### A modern ecosystem

Hugo's theme community is active, innovative, and built around modern tooling. This is where Blowfish really shines.

## Choosing a Theme

I settled on the [Blowfish](https://blowfish.page/) theme for several reasons. Honestly, it is one of the best examples of what Hugo makes possible.

{{< figure src="images/logos/blowfish-logo.png" alt="Blowfish illustration" class="mx-auto" width="260" >}}

### Clean, modern design

Blowfish looks great out of the box, with thoughtful typography, spacing, and layout options.

### Dark mode support

Automatic dark and light mode, user-selectable themes, and customizable color palettes are all built in.

### Feature-rich components

Blowfish includes components like:

- Callouts
- Cards
- Tabs
- Accordions
- Grids
- Footnotes
- Copy-to-clipboard code blocks

These let you build richer content without custom HTML.

### Built-in image optimization

Thanks to Hugo's image pipeline, Blowfish can automatically resize, crop, optimize, lazy-load, and serve responsive images. This is something Jekyll cannot match without external tooling.

### Taxonomies and structure

Categories, tags, sections, menus, and breadcrumbs work cleanly and consistently.

### Active development and documentation

Blowfish is well maintained, well documented, and constantly improving.

### Tailwind CSS for customization

If you want to tweak the design, Tailwind makes it straightforward.

## Jekyll vs. Hugo (with Blowfish): A Practical Comparison

| Feature / Area | Jekyll | Hugo (with Blowfish) |
|---|---|---|
| Build Speed | Slow on larger sites; rebuilds often 20-60 seconds | Extremely fast; rebuilds typically under 1 second |
| Dependencies | Requires Ruby, Bundler, gems, and version management | Single binary, no external dependencies |
| Templating System | Liquid (simple but limited) | Go templates (powerful, flexible, feature-rich) |
| Image Processing | Not built in; requires external tools or plugins | Native image pipeline: resize, crop, optimize, responsive images |
| Theme Ecosystem | Many themes, but many feel dated or unmaintained | Modern themes with active development; Blowfish is a standout |
| Dark Mode Support | Theme-dependent; often limited | Built-in automatic dark/light mode plus user theme switching |
| Content Components | Limited; requires plugins or custom HTML | Blowfish includes cards, callouts, tabs, accordions, grids, and more |
| Search | Requires external JS libraries or plugins | Blowfish includes fast, built-in client-side search |
| Multilingual Support | Plugin-based, inconsistent | First-class multilingual support built into Hugo |
| Taxonomies | Basic categories/tags | Flexible taxonomies, sections, menus, breadcrumbs |
| Asset Pipeline | Basic; often requires plugins | Built-in minification, fingerprinting, and processing |
| Customization | Varies by theme; often requires manual CSS | Blowfish uses Tailwind for easy, modern customization |
| Documentation | Good but plugin-heavy | Excellent docs; Blowfish has strong theme documentation |
| Local Development | Slower reloads; can feel laggy | Instant hot reload; smooth editing experience |
| CI/CD | Slower builds; Ruby setup required | Fast builds; no setup beyond Hugo binary |
| Learning Curve | Easy to start, harder to extend | Easy to start, powerful as you grow |

## Results

After migrating, a few wins stood out:

- **Build time**: Dropped from 30+ seconds to under 1 second
- **No dependencies**: Just the Hugo binary, nothing else
- **Better DX**: Hot reload is nearly instant
- **Modern design**: Blowfish looks great on all devices
- **More flexibility**: Shortcodes, components, and image processing make content creation easier

Overall, the site feels faster, cleaner, and more maintainable.

## What's Next

In Part 2, I'll cover the actual migration process:

- Converting posts
- Fixing front matter
- Replacing Jekyll shortcodes
- Handling images and static assets
- Structuring content for Hugo's taxonomy system

If you're considering making the switch yourself, the migration is easier than you might think.

## Resources

- [Hugo Documentation](https://gohugo.io/documentation/)
- [Blowfish Theme](https://blowfish.page/)
- [Jekyll to Hugo Migration Guide](https://gohugo.io/tools/migrations/#jekyll)

