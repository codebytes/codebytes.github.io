---
title: "Headless CMS Without a PC on GitHub Pages"
date: 2025-06-26
tags:
    - GitHub Pages
    - Sveltia CMS
    - Cloudflare Workers
    - Mobile
    - CMS
categories: 
    - Web Development
    - Tools
permalink: /2025/06/26/mobile-cms-on-github-pages/
header:
  teaser: /assets/images/sveltia-cms.png
  og_image: /assets/images/sveltia-cms.png
excerpt_separator: "<!--more-->"
---

Headless CMS Without a PC on GitHub Pages

I've been running my site on GitHub Pages - no server, just git and GitHub Actions. But I still want a CMS that works on mobile, without dragging around a laptop or doing a Git clone. Enter [Sveltia CMS](https://github.com/sveltia/sveltia-cms) + [Sveltia CMS Auth](https://github.com/sveltia/sveltia-cms-auth) on Cloudflare Workers. Here's how to glue it together.

<!--more-->

## Why This Setup?
- No paid services like Netlify.
- I edit blog posts from my phone-even waiting in line for coffee.
- No git install, no desktop.

A solution exists: [Sveltia's Cloudflare Workers-based authenticator](https://github.com/sveltia/sveltia-cms-auth) makes GitHub-backed CMS possible on [GitHub Pages](https://pages.github.com/).

## 🎯 Step 1: Add Sveltia CMS to Your Site

In your /admin/index.html, include Sveltia, a lightweight, modern CMS:

```html
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="noindex" />
    <title>Content Manager</title>
</head>

<body>
    <script src="https://unpkg.com/@sveltia/cms/dist/sveltia-cms.js"></script>
</body>

</html>
```

No heavy JS, no React-just [Svelte](https://svelte.dev/). Touch support, dark mode, fast. It handles GitHub directly via your browser or the auth worker.

## 🔐 Step 2: Deploy the Sveltia-CMS-Auth Worker
1. Fork or import [sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth) into [Cloudflare Workers](https://workers.cloudflare.com/).
2. Deploy it; grab the Worker URL.
3. Register a [GitHub OAuth App](https://github.com/settings/applications/new), using the Worker URL plus /callback for the redirect.
4. Add client credentials and your domain to Workers environment variables. Deploy again.

Now your site has its own auth client-it communicates with GitHub when you click Login.

## 🛠 Step 3: Wire It All Up in Your Config

In your Sveltia admin/config.yml, under backend:

```yaml
backend:
  name: github
  repo: <OWNER>/<REPO> # Path to your GitHub repository
  # optional, defaults to master
  branch: main
  base_url: https://<WORKER>.workers.dev
# This line should *not* be indented
media_folder: "assets/uploads" # Media files will be stored in the repo under images/uploads
```

That base_url points Sveltia's OAuth to your Worker. Push the change, and your /admin/ loads Sveltia. Clicking "Login" redirects to GitHub via your Worker, and you're ready to edit.

## 📱 Step 4: Edit From Your Phone

Visit yourgithubpages.com/admin/ on your mobile device. The UI is responsive and built for touch. I've easily edited blog posts without needing VS Code or Terminal. Sveltia handles commit and push transparently.

## Quick FAQ

**Q: Why not Decap CMS or Netlify CMS?**  
A: They typically rely on external OAuth providers. [Sveltia](https://github.com/sveltia/sveltia-cms) + Cloudflare Workers solves that neatly.

**Q: Does it require a PC?**  
A: Only initial setup needs a desktop. Afterward, your CMS runs entirely in-browser, even mobile.

**Q: Self-hosted?**  
A: [GitHub Pages](https://docs.github.com/en/pages) hosts the static site. The CMS runs client-side, and auth is on [Cloudflare's free tier](https://developers.cloudflare.com/workers/platform/pricing/).

## TL;DR

| Goal | Tool |
|------|------|
| GitHub-only hosting | [GitHub Pages](https://pages.github.com/) (no server) |
| Modern, touch-ready UI | [Sveltia CMS](https://github.com/sveltia/sveltia-cms) |
| OAuth via GitHub | [Sveltia-CMS-Auth Worker](https://github.com/sveltia/sveltia-cms-auth) |
| Zero laptop edits | Fully mobile browser-compatible |

This combo gives me a mobile-friendly CMS experience without extra hassle. If you're editing your [Jekyll-based GitHub Pages blog](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll) without a PC, this setup hits the mark.

## Related Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Setting up Custom Domains with GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [Managing Multiple Domains with Cloudflare](https://developers.cloudflare.com/dns/manage-dns-records/)
- [Sveltia CMS GitHub Repository](https://github.com/sveltia/sveltia-cms)
- [Sveltia CMS Auth GitHub Repository](https://github.com/sveltia/sveltia-cms-auth)
- [My Previous Post on Migrating to GitHub Pages](/2022/12/20/migrating-from-wordpress-to-github-pages)
- [My Guide to Multiple Domains on GitHub Pages](/2022/12/27/multiple-domains-on-github-pages)