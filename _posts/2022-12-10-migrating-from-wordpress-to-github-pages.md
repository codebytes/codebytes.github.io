---
title: Migrating from WordPress to GitHub Pages
type: post
categories:
- Development
tags:
- dotnet
- configuration
permalink: /2022/12/10/migrating-from-wordpress-to-github-pages
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
I exported all my posts from Wordpress.com (about 20). It also imported all my images, but they had many duplicates. Some image URLs had both normal URLs (“/blah/image.jpg”) but some had other URLs (“/blah/image.jpg@60px”). After this import process, I touched up each post and image.