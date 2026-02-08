---
title: "Migrating from Jekyll to Hugo Part 2: Content Migration"
date: '2026-01-18'
draft: false
categories:
  - Blog
tags:
  - Hugo
  - Jekyll
  - Markdown
  - Mermaid
description: "How I migrated content from Jekyll to Hugo - front matter, shortcodes, and assets."
featureimage: "images/logos/hugo-logo.svg"
---

In Part 1, I covered why I switched from Jekyll to Hugo. Now let's dive into the actual content migration.

<!--more-->

## Front Matter Conversion

Most Jekyll posts work with minimal changes, but there are key differences:

```yaml
# Jekyll
---
layout: post
title: "My Post"
date: 2024-01-15
categories: development
tags: [docker, containers]
mermaid: true
---

# Hugo
---
title: "My Post"
date: 2024-01-15
categories:
  - Development
tags:
  - Docker
  - Containers
---
```

Key changes I made:

- **Removed `layout: post`** - Hugo infers layout from content location
- **Converted tags/categories to arrays** - YAML list format
- **Standardized capitalization** - Consistent taxonomy naming
- **Removed `mermaid: true`** - Blowfish auto-detects mermaid shortcodes

{{< alert "lightbulb" >}}
**Tip:** Run `hugo server` while migrating so you can preview each converted post immediately and catch front matter issues early.
{{< /alert >}}

## Shortcode Conversions

Jekyll uses Liquid templates while Hugo has its own shortcode system.

### Images and Figures

```markdown
<!-- Jekyll -->
{% include figure.html src="/images/photo.jpg" caption="My caption" %}

<!-- Hugo -->
{{</* figure src="/images/photo.jpg" caption="My caption" */>}}
```

Here's the Hugo figure shortcode in action:

{{< figure src="images/logos/hugo-logo.svg" alt="Hugo Logo" caption="The Hugo logo rendered with the figure shortcode" class="mx-auto" width="200" >}}

### Mermaid Diagrams

This was a bigger change. Jekyll with the mermaid plugin uses fenced code blocks:

````markdown
<!-- Jekyll -->
```mermaid
graph TD
    A --> B
```
````

Hugo with Blowfish requires the mermaid shortcode:

```markdown
<!-- Hugo -->
{{</* mermaid */>}}
graph TD
    A --> B
{{</* /mermaid */>}}
```

I wrote a quick script to find and convert these across all posts. Here's what a real mermaid diagram looks like after migration:

{{< mermaid >}}
flowchart LR
    A["Jekyll Post\n(.md + Liquid)"] -->|migrate| B["Hugo Post\n(.md + Shortcodes)"]
    B --> C{"hugo build"}
    C --> D["Static HTML"]
    C --> E["Processed Images"]
    C --> F["Minified CSS/JS"]
{{< /mermaid >}}

### Code Blocks

Standard fenced code blocks work the same, but Hugo adds features:

```markdown
<!-- Hugo with line numbers -->
{{</* highlight go "linenos=table,hl_lines=3" */>}}
func main() {
    fmt.Println("Hello")
    fmt.Println("Highlighted!")
}
{{</* /highlight */>}}
```

Here's what that looks like rendered with Hugo's syntax highlighting and line numbers:

{{< highlight go "linenos=table,hl_lines=3" >}}
func main() {
    fmt.Println("Hello")
    fmt.Println("Highlighted!")
}
{{< /highlight >}}

## Static Assets

Jekyll and Hugo organize assets differently:

| Jekyll | Hugo |
|--------|------|
| `assets/images/` | `static/images/` |
| `_data/` | `data/` |
| `_includes/` | `layouts/partials/` |

For images referenced in posts, I kept paths like `/images/photo.jpg` which maps to `static/images/photo.jpg`.

{{< alert >}}
**Watch out:** Hugo's `assets/` folder is for files processed by Hugo Pipes (SCSS, image resizing, fingerprinting). Use `static/` for files served as-is. Mixing them up leads to 404s.
{{< /alert >}}

## Handling Excerpts

Jekyll uses `excerpt_separator` in config or `<!--more-->` in posts. Hugo works the same way with `<!--more-->`:

```markdown
---
title: "My Post"
---

This appears in the summary.

<!--more-->

This is the full content.
```

## Taxonomy Cleanup

I took the opportunity to consolidate tags:

- Merged similar tags (`vscode` → `VSCode`)
- Standardized capitalization
- Removed unused categories

## Bulk Migration Script

> "The best migration is the one you automate. Don't hand-edit 60 posts when a script can do it in seconds."

For 60+ posts, I used a simple PowerShell script:

```powershell
Get-ChildItem "content/posts/*.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    
    # Remove layout: post
    $content = $content -replace "layout: post\r?\n", ""
    
    # Remove mermaid: true
    $content = $content -replace "mermaid: true\r?\n", ""
    
    Set-Content $_.FullName $content
}
```

{{< alert "circle-info" >}}
**Note:** The PowerShell script above covers the basics, but you may need additional passes for things like Liquid `{% raw %}` blocks or custom Jekyll includes. Test thoroughly!
{{< /alert >}}

## What's Next

In Part 3, I'll cover deployment with GitHub Actions and the challenges I encountered along the way.

## Resources

- [Hugo Content Organization](https://gohugo.io/content-management/organization/)
- [Hugo Shortcodes](https://gohugo.io/content-management/shortcodes/)
- [Blowfish Shortcodes](https://blowfish.page/docs/shortcodes/)
