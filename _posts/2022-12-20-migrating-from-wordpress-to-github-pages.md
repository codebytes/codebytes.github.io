---
title: Migrating from WordPress to GitHub Pages
type: post
categories:
- Development
tags:
- wordpress
- jekyll
- GitHub
- markdown
- ruby
permalink: /2022/12/20/migrating-from-wordpress-to-github-pages
---

I’ve been hosting on WordPress for a while. I wanted something that worked pretty well and was easy to work with. I picked a decent theme, added some plugins, pointed my domains and was up and running. I would work on blogs in MarkDown, and then paste the txt into a MarkDown. I could upload a few images and move them around in a wysiwyg.

Lately, I’ve been doing a lot more in MarkDown. All my conference talks were in PowerPoint but I’ve started switching over to MarkDown slides using MARP.  I should probably do a post on MARP sometime. I wanted to reduce my overhead of WordPress Hosting and get back into more direct styling and coding of my theme.  I decided to switch my hosting to Jekyll on GitHub Pages.
	
## Setting Up GitHub Pages

There are great docs on how to setup Jekyll with GitHub Pages.
- https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll
First this is I setup a repo to host my page.  My username is codebytes, so I made a repo for codebytes.github.io. 
- https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site#creating-a-repository-for-your-site

Knowing that I’m going to be using this repo for a Jekyll based site, I setup a dev container so that I could quickly have all the tools setup and configured.
https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/creating-a-github-pages-site-with-jekyll

## Setting Up Jekyll

I used the Jekyll theme called “Minimal Mistakes”. https://mademistakes.com/work/jekyll-themes/minimal-mistakes/. 

I used the Jekyll-import. Because of the plan I was using on WordPress.com, I couldn’t install custom extensions. That eliminated many export/import options. There is a free option for importing things into Jekyll-import using a Wordpress.xml export file.
https://import.jekyllrb.com/docs/wordpressdotcom/

Since I'm using a devcontainer for my local blog, I setup Jekyll-import and its dependencies. I added the dependencies to the local gemfile and ran bundle install.

```ruby
  gem "hpricot"
  gem "open_uri_redirections"
  gem "safe_yaml"
  gem "jekyll-import"
```

```bash
bundle install
```

On Wordpress.com I exported all my posts via the export functionality.
![Export Menu](/assets/2022/12/wordpress-export-tools.png)

I then Exported everything which downloads as a single file.
![Export Option](/assets/2022/12/wordpress-export.png)

This provides an download that's a zip file with an xml file.  I ran the import command:

```bash
bundle exec jekyll import wordpressdotcom --source wordpress.export.xml --assets_folder assets/
```

I imported all my posts from Wordpress.com (about 20). It also imported all my images, but they had many duplicates. Some image URLs had both normal URLs (“/blah/image.jpg”) but some had other URLs (“/blah/image.jpg@60px”). After this import process, I touched up each post and image.

For each post I had to resolve the front matter at the top of each post.  Imported it looked like this:

```md
---
layout: post
title: 'ARM - Part 1: Azure Resource Manager'
date: 2019-05-11 23:53:57.000000000 +00:00
type: post
parent_id: '0'
published: true
password: ''
status: publish
categories:
- DevOps
tags:
- arm
- arm templates
- azure
- cli
- infrastructure
- Microsoft
- PowerShell
- scripts
meta:
  _wpas_skip_571772: '1'
  _publicize_done_21771511: '1'
  publicize_linkedin_url: ''
  _publicize_job_id: '30717764168'
  timeline_notification: '1557633304'
  _publicize_done_external: a:2:{s:7:"twitter";a:1:{i:22482724;s:60:"https://twitter.com/Chris_L_Ayers/status/1127421911250677761";}s:8:"facebook";a:1:{i:22482726;s:52:"https://facebook.com/482199522523634_482213102522276";}}
  _wpas_done_22482724: '1'
  publicize_twitter_user: Chris_L_Ayers
  _publicize_done_21771513: '1'
  _wpas_done_22482728: '1'
  _publicize_done_21801094: '1'
  _wpas_done_22482726: '1'
author:
  login: chrislayers
  email: EMAIL
  display_name: Chris Ayers
  first_name: Chris
  last_name: Ayers
permalink: "/2019/05/11/arm-azure-resource-manager/"
---
```

After cleaning it up the front matter is much clearer.

```md
---
title: 'ARM - Part 1: Azure Resource Manager'
date: 2019-05-11 23:53:57.000000000 +00:00
type: post
categories:
- DevOps
tags:
- arm
- arm templates
- azure
- cli
- infrastructure
- Microsoft
- PowerShell
- scripts
permalink: "/2019/05/11/arm-azure-resource-manager/"
---
```

I similarly had to clean up some of the html in the imported posts.  Mainly I removed a bunch of the commented html and converted it all to markdown.

```html
<p><!-- wp:heading {"level":3} --></p>
<h3>The Journey Begins</h3>
<p><!-- /wp:heading --></p>
```

That got cleaned up to and looking good in with markdown preview:

```md
### The Journey Begins
```

Finally, I reviewed each image and cleaned up the references.

```html
<p><!-- wp:image {"id":151} --></p>
<figure class="wp-block-image"><img src="{{ site.baseurl }}/assets/2019/05/newresourcegroup-3.png?w=936" alt="" class="wp-image-151" /></figure>
<p><!-- /wp:image --></p>
```

The theme [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/docs/helpers/#figure) has great helpers for figures and images. I converted the html to markdown using the figure helper like this:

{% raw %}
```md
{% include figure image_path="/assets/2019/05/newresourcegroup-3.png" alt="A new Azure Resource Group." caption="A new Azure Resource Group." %}
```
{% endraw %}

I spent a few hours, fixed all the front matter and naming, converted all html to markdown, then removed and renamed old images. 

I was able to test locally by running running ```jekyll serve``` and checking how everything looked in a browser.
```bash
bundle exec jekyll serve
```

As part of setting up things with GitHub Pages, there is also a workflow that helps build and release the jeykll site to GitHub pages.

I'll follow this up with another post on some of my customizations for monitoring and dns. Out of the box, GitHub pages only allow 1 custom dns domain. There are a few ways to host multiple domains on a single GitHub Pages site (check out [chrislayers.com](https://chrislayers.com), [chrisayers.me](https://chrisayers.me), or [chris-ayers.com](https://chris-ayers.com)).
