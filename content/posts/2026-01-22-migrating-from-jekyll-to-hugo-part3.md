---
title: "Migrating from Jekyll to Hugo Part 3: Deployment and Lessons Learned"
date: 2026-01-22
draft: true
categories:
  - Blog
tags:
  - Hugo
  - GitHub Pages
  - GitHub Actions
  - DevOps
description: "Setting up GitHub Actions for Hugo deployment and lessons learned from the migration."
---

In the final part of this series, I cover deploying Hugo to GitHub Pages and share the challenges I encountered.

<!--more-->

## GitHub Actions Workflow

Here's the workflow I use to deploy Hugo to GitHub Pages:

```yaml
name: Deploy Hugo site to Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true

      - name: Setup Pages
        uses: actions/configure-pages@v5

      - name: Build
        env:
          HUGO_CACHEDIR: ${{ runner.temp }}/hugo_cache
          HUGO_ENVIRONMENT: production
          TZ: America/New_York
        run: hugo --gc --minify --baseURL "${{ steps.pages.outputs.base_url }}/"

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

Key points:

- **`submodules: recursive`** - Required for theme as submodule
- **`fetch-depth: 0`** - Needed for `.GitInfo` and `.Lastmod`
- **`extended: true`** - Required for SCSS/Sass processing
- **`--gc --minify`** - Clean up and optimize output

## Challenges and Solutions

### Challenge 1: Preserving URLs

Jekyll and Hugo generate different URL structures. To avoid breaking existing links, I used Hugo aliases:

```yaml
# In front matter
aliases:
  - /category/development/my-old-post-url/
```

For bulk redirects, I created `static/_redirects` for Netlify-style redirects (works with some hosts).

### Challenge 2: Theme Version Compatibility

I hit this warning early on:

```text
WARN Module "blowfish" is not compatible with this Hugo version
```

**Solution**: Pin both Hugo and theme versions:

```yaml
# In GitHub Actions
hugo-version: '0.140.2'
```

```bash
# Pin theme to specific commit
cd themes/blowfish
git checkout v2.52.0
```

### Challenge 3: Date Formatting

Hugo uses Go's reference time format. This tripped me up:

```go
// Go reference: Mon Jan 2 15:04:05 MST 2006
{{ .Date.Format "January 2, 2006" }}   // January 20, 2025
{{ .Date.Format "2006-01-02" }}         // 2025-01-20
```

### Challenge 4: Custom Layouts

Some Jekyll layouts needed recreation. Hugo's template lookup order:

1. `layouts/<type>/<layout>.html`
2. `layouts/_default/<layout>.html`
3. Theme equivalents

I started by copying theme layouts to my `layouts/` folder and customizing.

### Challenge 5: RSS Feed URLs

Jekyll's feed was at `/feed.xml`, Hugo's default is `/index.xml`. I added an alias:

```toml
# config.toml
[outputFormats.RSS]
  baseName = "feed"
```

## Tips for Your Migration

1. **Start fresh** - Create new Hugo site, don't convert in place
2. **Migrate incrementally** - Move posts in batches, test as you go
3. **Use `hugo server -D`** - Shows drafts with hot reload
4. **Read theme docs** - Blowfish has excellent documentation
5. **Test all pages** - Especially taxonomy and archive pages
6. **Check mobile** - Verify responsive design works
7. **Validate feeds** - Test RSS/Atom with a feed reader

## Before and After

| Metric | Jekyll | Hugo |
|--------|--------|------|
| Build time | 30+ seconds | < 1 second |
| Dependencies | Ruby, Bundler, gems | Single binary |
| Hot reload | Slow | Instant |
| Theme options | Limited | Extensive |

## Conclusion

The migration took a weekend of focused work, but it was absolutely worth it. Hugo's speed and flexibility have made maintaining this blog much more enjoyable.

The key is taking it step by step:

1. Set up Hugo with your chosen theme
2. Migrate content in batches
3. Fix shortcodes and assets
4. Set up deployment
5. Test thoroughly before switching DNS

If you're considering the switch, I hope this series helps. Feel free to reach out with questions!

## Resources

- [Hugo Documentation](https://gohugo.io/documentation/)
- [Blowfish Theme](https://blowfish.page/)
- [Hugo on GitHub Pages](https://gohugo.io/hosting-and-deployment/hosting-on-github/)
- [Jekyll to Hugo Migration](https://gohugo.io/tools/migrations/#jekyll)
