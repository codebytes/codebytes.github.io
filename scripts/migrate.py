#!/usr/bin/env python3
"""
Jekyll to Hugo Migration Script

Converts Jekyll posts from _posts/ and _drafts/ to Hugo format in content/posts/
Handles front matter conversion and generates aliases for old URLs.
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime

# Source and destination directories
JEKYLL_POSTS = Path("_posts")
JEKYLL_DRAFTS = Path("_drafts")
HUGO_POSTS = Path("hugo-site/content/posts")

def parse_jekyll_post(filepath):
    """Parse a Jekyll post and extract front matter and content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match YAML front matter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if not match:
        print(f"Warning: No front matter found in {filepath}")
        return None, content
    
    front_matter_str = match.group(1)
    body = match.group(2)
    
    try:
        front_matter = yaml.safe_load(front_matter_str)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {filepath}: {e}")
        return None, body
    
    return front_matter, body

def get_slug_from_filename(filename):
    """Extract slug from Jekyll filename (YYYY-MM-DD-slug.md)."""
    # Remove date prefix and extension
    match = re.match(r'\d{4}-\d{2}-\d{2}-(.+)\.md$', filename)
    if match:
        return match.group(1)
    return filename.replace('.md', '')

def get_date_from_filename(filename):
    """Extract date from Jekyll filename."""
    match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None

def generate_old_url(front_matter, filename):
    """Generate the old Jekyll URL for aliasing."""
    aliases = []
    
    # Check for explicit permalink
    if 'permalink' in front_matter:
        permalink = front_matter['permalink']
        if not permalink.endswith('/'):
            permalink += '/'
        aliases.append(permalink)
    
    # Check for redirect_from
    if 'redirect_from' in front_matter:
        redirects = front_matter['redirect_from']
        if isinstance(redirects, str):
            redirects = [redirects]
        for r in redirects:
            if not r.endswith('/'):
                r += '/'
            if r not in aliases:
                aliases.append(r)
    
    # Generate category-based URL (Jekyll default: /:categories/:title/)
    categories = front_matter.get('categories', [])
    slug = get_slug_from_filename(filename)
    
    if categories:
        if isinstance(categories, str):
            categories = [categories]
        # Jekyll uses lowercase categories in URLs
        cat_path = '/'.join(c.lower() for c in categories)
        old_url = f"/{cat_path}/{slug}/"
        if old_url not in aliases:
            aliases.append(old_url)
    
    return aliases

def convert_front_matter(jekyll_fm, filename, is_draft=False):
    """Convert Jekyll front matter to Hugo format."""
    hugo_fm = {}
    
    # Title
    if 'title' in jekyll_fm:
        hugo_fm['title'] = jekyll_fm['title']
    else:
        # Generate from filename
        slug = get_slug_from_filename(filename)
        hugo_fm['title'] = slug.replace('-', ' ').title()
    
    # Date
    if 'date' in jekyll_fm:
        date = jekyll_fm['date']
        if isinstance(date, datetime):
            hugo_fm['date'] = date.strftime('%Y-%m-%dT%H:%M:%S%z') or date.strftime('%Y-%m-%d')
        else:
            hugo_fm['date'] = str(date)
    else:
        date_from_file = get_date_from_filename(filename)
        if date_from_file:
            hugo_fm['date'] = date_from_file
    
    # Draft status
    if is_draft:
        hugo_fm['draft'] = True
    
    # Categories
    if 'categories' in jekyll_fm:
        cats = jekyll_fm['categories']
        if isinstance(cats, str):
            cats = [cats]
        hugo_fm['categories'] = cats
    
    # Tags
    if 'tags' in jekyll_fm:
        tags = jekyll_fm['tags']
        if isinstance(tags, str):
            tags = [tags]
        hugo_fm['tags'] = tags
    
    # Summary/Description
    if 'excerpt' in jekyll_fm:
        hugo_fm['summary'] = jekyll_fm['excerpt']
    elif 'description' in jekyll_fm:
        hugo_fm['summary'] = jekyll_fm['description']
    
    # Featured image
    if 'header' in jekyll_fm:
        header = jekyll_fm['header']
        if isinstance(header, dict):
            if 'teaser' in header:
                # Convert Jekyll asset path to Hugo static path
                teaser = header['teaser']
                teaser = teaser.replace('/assets/images/', '/images/')
                hugo_fm['image'] = teaser
            if 'og_image' in header:
                og = header['og_image']
                og = og.replace('/assets/images/', '/images/')
                hugo_fm['featureImage'] = og
    
    # Mermaid support
    if jekyll_fm.get('mermaid'):
        hugo_fm['mermaid'] = True
    
    # TOC
    if jekyll_fm.get('toc'):
        hugo_fm['showTableOfContents'] = True
    
    # Generate aliases for old URLs
    aliases = generate_old_url(jekyll_fm, filename)
    if aliases:
        hugo_fm['aliases'] = aliases
    
    # Slug (explicit)
    hugo_fm['slug'] = get_slug_from_filename(filename)
    
    return hugo_fm

def convert_content(body):
    """Convert Jekyll-specific content to Hugo format."""
    # Convert Jekyll include syntax to Hugo shortcodes where applicable
    # {% include figure image_path="..." %} -> {{< figure src="..." >}}
    body = re.sub(
        r'\{%\s*include\s+figure\s+image_path="([^"]+)"([^%]*)\s*%\}',
        r'{{< figure src="\1" >}}',
        body
    )
    
    # Update asset paths
    body = body.replace('/assets/images/', '/images/')
    body = body.replace('/assets/headshot/', '/images/')
    
    # Convert Jekyll highlight blocks to Hugo
    # {% highlight lang %} -> ```lang
    body = re.sub(r'\{%\s*highlight\s+(\w+)\s*%\}', r'```\1', body)
    body = re.sub(r'\{%\s*endhighlight\s*%\}', r'```', body)
    
    # Convert Jekyll raw blocks
    body = re.sub(r'\{%\s*raw\s*%\}', '', body)
    body = re.sub(r'\{%\s*endraw\s*%\}', '', body)
    
    return body

def write_hugo_post(hugo_fm, body, output_path):
    """Write the converted post to Hugo format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('---\n')
        yaml.dump(hugo_fm, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        f.write('---\n')
        f.write(body)
    
    print(f"  -> {output_path}")

def migrate_posts(source_dir, is_draft=False):
    """Migrate all posts from source directory."""
    if not source_dir.exists():
        print(f"Source directory {source_dir} not found, skipping...")
        return
    
    posts = list(source_dir.glob('*.md'))
    print(f"\nMigrating {len(posts)} {'drafts' if is_draft else 'posts'} from {source_dir}...")
    
    for post_path in sorted(posts):
        print(f"Processing: {post_path.name}")
        
        jekyll_fm, body = parse_jekyll_post(post_path)
        if jekyll_fm is None:
            jekyll_fm = {}
        
        hugo_fm = convert_front_matter(jekyll_fm, post_path.name, is_draft)
        converted_body = convert_content(body)
        
        # Output filename (keep the same for now)
        output_path = HUGO_POSTS / post_path.name
        write_hugo_post(hugo_fm, converted_body, output_path)

def migrate_assets():
    """Copy assets to Hugo static directory."""
    import shutil
    
    source_assets = Path("assets/images")
    dest_assets = Path("hugo-site/static/images")
    
    if source_assets.exists():
        print(f"\nCopying assets from {source_assets} to {dest_assets}...")
        dest_assets.mkdir(parents=True, exist_ok=True)
        
        for item in source_assets.iterdir():
            dest = dest_assets / item.name
            if item.is_file():
                shutil.copy2(item, dest)
                print(f"  -> {dest}")
            elif item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
                print(f"  -> {dest}/")
    
    # Copy headshot/avatar
    source_headshot = Path("assets/headshot")
    if source_headshot.exists():
        print(f"\nCopying headshot from {source_headshot}...")
        for item in source_headshot.iterdir():
            dest = dest_assets / item.name
            if item.is_file():
                shutil.copy2(item, dest)
                print(f"  -> {dest}")

def main():
    """Main migration function."""
    print("=" * 60)
    print("Jekyll to Hugo Migration")
    print("=" * 60)
    
    # Ensure Hugo content directory exists
    HUGO_POSTS.mkdir(parents=True, exist_ok=True)
    
    # Migrate published posts
    migrate_posts(JEKYLL_POSTS, is_draft=False)
    
    # Migrate drafts
    migrate_posts(JEKYLL_DRAFTS, is_draft=True)
    
    # Migrate assets
    migrate_assets()
    
    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review migrated posts in hugo-site/content/posts/")
    print("2. Check for any conversion issues")
    print("3. Run 'cd hugo-site && hugo server' to test")

if __name__ == "__main__":
    main()
