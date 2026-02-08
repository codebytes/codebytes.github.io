---
title: "Migrating from Jekyll to Hugo Part 3: Deployment and Lessons Learned"
date: '2026-01-25'
draft: false
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
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    env:
      HUGO_VERSION: 0.155.3
    steps:
      - name: Checkout
        uses: actions/checkout@8e8c483db84b4bee # v6.0.2
        with:
          fetch-depth: 0
          persist-credentials: false
          submodules: recursive

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@75d2e847 # v3.0.0
        with:
          hugo-version: ${{ env.HUGO_VERSION }}
          extended: true

      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@983d7736 # v5.0.0

      - name: Cache Hugo resources
        uses: actions/cache@8b402f58 # v5.0.3
        with:
          path: |
            ${{ runner.temp }}/hugo_cache
            resources/_gen
          key: hugo-${{ runner.os }}-${{ hashFiles('content/**', 'config/**', 'assets/**') }}
          restore-keys: |
            hugo-${{ runner.os }}-

      - name: Build with Hugo
        env:
          HUGO_CACHEDIR: ${{ runner.temp }}/hugo_cache
          HUGO_ENVIRONMENT: production
          TZ: America/New_York
        run: |
          hugo \
            --gc \
            --minify \
            --baseURL "${{ steps.pages.outputs.base_url }}/"

      - name: Upload artifact
        uses: actions/upload-pages-artifact@7b1f4a76 # v4.0.0
        with:
          path: ./public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@d6db9016 # v4.0.5
```

Key points:

- **SHA-pinned actions** - Every action is pinned to a commit SHA, not a mutable tag — critical for supply chain security
- **Scoped permissions** - Minimal permissions declared per-job, not at the workflow level
- **`submodules: recursive`** - Required for the theme submodule
- **`fetch-depth: 0`** - Needed for `.GitInfo` and `.Lastmod`
- **`persist-credentials: false`** - Security best practice for checkout
- **Pinned Hugo version** - `HUGO_VERSION` env var ensures reproducible builds
- **Caching** - Both `hugo_cache` and `resources/_gen` are cached to speed up builds
- **`--gc --minify`** - Clean up unused cache entries and optimize output

## Linting with Super-Linter

In addition to the deploy workflow, I added a [Super-Linter](https://github.com/super-linter/super-linter) workflow that runs on every PR:

```yaml
name: Super-Linter

on:
  pull_request: null

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    name: Lint
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: read
      statuses: write
    steps:
      - name: Checkout code
        uses: actions/checkout@8e8c483db84b4bee # v6.0.1
        with:
          fetch-depth: 0
          persist-credentials: false

      - name: Super-linter
        uses: super-linter/super-linter@d5b0a2ab # v8.3.2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          VALIDATE_ALL_CODEBASE: 'false'
          # Auto-fix formatting on PR
          FIX_CSS_PRETTIER: 'true'
          FIX_HTML_PRETTIER: 'true'
          FIX_JSON_PRETTIER: 'true'
          FIX_MARKDOWN_PRETTIER: 'true'
          FIX_YAML_PRETTIER: 'true'
          # Disable linters that don't apply
          VALIDATE_JSCPD: 'false'
          VALIDATE_PYTHON: 'false'
          # Use repo markdownlint config
          MARKDOWN_CONFIG_FILE: '.markdownlint.yml'
          # Don't lint the theme submodule
          FILTER_REGEX_EXCLUDE: 'themes/.*'
```

This catches markdown issues, YAML errors, and formatting problems before they hit `main`. The `FIX_*` options automatically commit formatting corrections back to the PR branch, which saves a lot of manual cleanup. I exclude the `themes/` directory since that's third-party code.

I also keep linting config files in the repo root:

- `.markdownlint.yml` - Disables rules like `MD013` (line length) and `MD033` (inline HTML — needed for Hugo shortcodes)
- `.yaml-lint.yml` - Warns on formatting issues without blocking
- `.textlintrc` - Terminology checks
- `.eslintrc.yml` - JavaScript linting for any custom scripts

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
env:
  HUGO_VERSION: 0.155.3
```

```bash
# Pin theme to specific tag
cd themes/blowfish
git checkout v2.97.0
```

### Challenge 3: Date Formatting

Hugo uses Go's reference time format. This tripped me up — Go doesn't use `YYYY-MM-DD` style format strings. Instead, it uses a specific reference time:

```text
Go reference time: Mon Jan 2 15:04:05 MST 2006
```

So in Hugo templates, you format dates like this:

```go-html-template
{{/* Long date */}}
{{ .Date.Format "January 2, 2006" }}
{{/* Output: January 25, 2026 */}}

{{/* ISO date */}}
{{ .Date.Format "2006-01-02" }}
{{/* Output: 2026-01-25 */}}

{{/* With time */}}
{{ .Date.Format "Jan 2, 2006 3:04 PM" }}
{{/* Output: Jan 25, 2026 12:00 AM */}}
```

The magic is that every component of the format is a specific number: month=1, day=2, hour=3, minute=4, second=5, year=6, timezone=7 (MST). Once you internalize that, it clicks.

### Challenge 4: Custom Layouts

Some Jekyll layouts needed recreation. Hugo's template lookup order:

1. `layouts/<type>/<layout>.html`
2. `layouts/_default/<layout>.html`
3. Theme equivalents

I started by copying theme layouts to my `layouts/` folder and customizing.

### Challenge 5: Split Config Files

Hugo supports splitting configuration across multiple files. Rather than one monolithic `config.toml`, I use a `config/_default/` directory:

```text
config/_default/
├── hugo.toml        # Core site settings
├── languages.en.toml
├── markup.toml      # Goldmark, syntax highlighting
├── menus.en.toml
├── module.toml
└── params.toml      # Theme parameters
```

This keeps things organized — especially as Blowfish has many configurable params. One thing that helped: setting `buildFuture = true` in `hugo.toml` so scheduled posts show up locally during development.

### Challenge 6: RSS Feed URLs

Jekyll's feed was at `/feed.xml`, but Hugo defaults to `/index.xml`. To avoid breaking existing subscribers, I configured Hugo to output both:

```toml
# hugo.toml
[outputs]
  home = ["HTML", "RSS", "FEED", "JSON"]

# Legacy feed.xml for backward compatibility with Jekyll
[outputFormats.FEED]
  mediaType = "application/rss+xml"
  baseName = "feed"
```

The custom `FEED` output format needs a matching template, so I copied the theme's `rss.xml` into my layouts:

```bash
cp themes/blowfish/layouts/_default/rss.xml layouts/_default/feed.xml
```

Now both `/index.xml` and `/feed.xml` are generated — existing subscribers keep working, and Hugo's default feed works too.

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
