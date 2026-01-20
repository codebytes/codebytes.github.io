---
title: "Migrating from Jekyll to Hugo Part 1: Why I Made the Switch"
date: 2025-01-20
draft: true
categories:
  - Blog
tags:
  - Hugo
  - Jekyll
  - GitHub Pages
  - Blowfish
description: "Why I moved this blog from Jekyll to Hugo and chose the Blowfish theme."
---

After years of running this blog on Jekyll, I finally made the switch to Hugo. Here's why.

<!--more-->

## Why I Made the Switch

Jekyll served me well for years, but a few pain points pushed me toward Hugo:

- **Build times**: As my site grew, Jekyll builds became noticeably slower
- **Ruby dependencies**: Managing Ruby versions and gems was sometimes frustrating
- **Theme flexibility**: I wanted more modern theme options with better dark mode support

Hugo promised faster builds, a single binary with no dependencies, and a vibrant theme ecosystem.

## Choosing a Theme

I settled on the [Blowfish](https://blowfish.page/) theme for several reasons:

- Clean, modern design
- Excellent dark mode support
- Built-in support for taxonomies (categories and tags)
- Active development and documentation
- Tailwind CSS for easy customization

## Results

After the migration:

- **Build time**: Dropped from 30+ seconds to under 1 second
- **No dependencies**: Just the Hugo binary
- **Better DX**: Hot reload is nearly instant
- **Modern design**: Blowfish looks great on all devices

## What's Next

In Part 2, I'll cover the actual content migration process - converting posts, fixing shortcodes, and handling assets.

## Resources

- [Hugo Documentation](https://gohugo.io/documentation/)
- [Blowfish Theme](https://blowfish.page/)
- [Jekyll to Hugo Migration Guide](https://gohugo.io/tools/migrations/#jekyll)
