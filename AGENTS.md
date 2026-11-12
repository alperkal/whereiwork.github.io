# Project context: Where I Work

## Purpose

This is Alper's personal photo blog about interesting places where he opened
his laptop and worked. The public website is https://wherei.work/.
Posts are intentionally minimal: a title, photograph, date, and location,
normally without body text. Preserve that focus when changing the site.

## Architecture and hosting

- Static Jekyll site based on the Millennial theme, with Liquid templates,
  Markdown/YAML content, Sass/CSS, and browser JavaScript.
- `Gemfile` loads `millennial.gemspec`, which specifies Jekyll `~> 4.2` and
  feed, pagination, sitemap, and SEO plugins. `jekyll-maps` is in `Gemfile`.
- Jekyll converts the source into HTML locally. Per the owner, production
  builds run through GitHub Pages/Actions, and GitHub Pages serves the result
  through the custom domain. `CNAME` contains `wherei.work`.
- `_config.yml` defines site metadata, plugins, collections, five posts per
  page, and post URLs using `/:title/`. AMP URLs use `/amp/:title/`.
- GitHub Pages settings and the latest successful deployment were not
  inspected; workflow files alone do not establish the live publishing mode.

## Repository map

| Path | Responsibility |
| --- | --- |
| `README.md` | Setup and post creation instructions |
| `_posts/YYYY-MM-DD-slug.md` | Main post source and location metadata |
| `_amp/` | Corresponding AMP post source |
| `_stories/main.md` | Generated AMP story source |
| `assets/img/` | Source photographs and other image assets |
| `assets/img/optimised/{320,640,960,1280,1600}/` | Generated responsive images |
| `assets/js/nodes.js` | Generated map location data |
| `assets/js/map.js` | Browser map behavior |
| `index.html`, `_layouts/home.html` | Paginated homepage |
| `_layouts/`, `_includes/` | Page templates and shared components |
| `_sass/`, `assets/css/main.scss` | Theme styling |
| `_data/settings.yml` | Navigation, social links, UI labels, comments |
| `pages/about.md`, `pages/map.md` | About and map pages |
| `rss-feed.xml` | Custom RSS feed with images; plugin also provides Atom feed |
| `today/index.html` | Existing static redirect to the homepage |
| `_site/` | Generated local build output; ignored by Git |
| `.github/workflows/` | Post automation and manual build workflows |

## Content conventions

Typical main post front matter (the date comes from the filename):

```yaml
---
layout: post
title: "Vienna - Random Cafe"
author: "Alper Kalaycioglu"
categories: whereiwork
tags: [documentation]
image: assets/img/example.jpg
amp: true
location:
  latitude: 48.2
  longitude: 16.3
---
```

The corresponding `_amp/` file uses `layout: amp` and `image: example.jpg`
(only the filename). Keep both versions consistent. Preserve existing slugs
and URLs when editing published posts.

## Local development

Run from the repository root:

```sh
gem install bundler
bundle install
bundle exec jekyll serve
```

Preview at http://localhost:4000. For a build-only check use
`bundle exec jekyll build`. `Gemfile.lock` is currently ignored and untracked,
so do not assume every environment resolves identical gem versions.
Some templates use `site.github.url` or hardcoded production URLs; when
previewing, check whether links and assets actually resolve locally.

## Adding posts

The README recommends `new_post.py` for local use:

```sh
python3 -m venv /tmp/whereiwork-venv
source /tmp/whereiwork-venv/bin/activate
pip install -r requirements.txt
python new_post.py assets/img/example.jpg "Vienna - Random Cafe"
```

Dependencies are Pillow and exifread. The script resizes the input image in
place to at most 1000px high, extracts EXIF date/GPS, creates main and AMP
posts, generates responsive images, and regenerates map data and the story.
Keep a separate original if needed. Calling it without arguments uses the
first file from `git diff --name-only HEAD^` and the latest commit message;
explicit arguments are more predictable.

The shell alternative is `./newPost.sh assets/img/example.jpg "Title"`.
It requires `exiftool`, ImageMagick, `jpegoptim`, and `optipng` (available
through Homebrew on macOS). It invokes `processMap.sh`,
`bash-responsive-images.sh`, and `createStories.sh`. `gitcheck.sh` accepts
an explicit image/title or derives them from Git.

Review the resulting image, post, AMP, map, and story changes before committing.
Do not run either generator just to inspect the project: they modify files.

## Checked-in automation

- `pushAction.yml` (New Post Flow): triggered by pushes affecting
  `assets/img/*` or manual dispatch. Uses the first added file and the commit
  message as the image/title, runs the **shell** pipeline, commits generated
  changes to `master`, and sends a Pushover status notification. Skips head
  commit messages containing `jekyl`. It does not itself run a Jekyll build.
- `jekyll.yml`: manual dispatch with filename/title inputs; runs
  `gitcheck.sh`, then `helaili/jekyll-action@2.3.1` targeting `master`.
- `jekyll-rebuild.yml`: manual dispatch that runs the same Jekyll action
  targeting `master`, without creating a post.

The Python helper has not replaced the shell pipeline in CI. Do not assume
that an arbitrary source push triggers the checked-in build workflows.
Check the current branch and remote Pages configuration before deployment
changes; the workflows explicitly target `master`.

## Known implementation details to recheck when relevant

- Generators assume `.jpg` in generated post image references. Use lowercase
  `.jpg` sources unless extending and validating other formats.
- Missing EXIF dates become `UNKNOWN` in the Python filename; missing GPS
  becomes empty coordinates. These need correction before publication.
- Python map generation includes the date in link paths, despite the
  `/:title/` permalink configuration; the shell version strips the date.
  Verify map links when using or changing the Python helper.
- Final story generation in Python and `createStories.sh` uses the latest
  filename as the cover, followed by up to ten entries in ascending filename
  order. The README's description of only recent posts is not exact.
- Existing responsive image files are skipped by the Python helper; replacing
  a source photo does not automatically refresh those derivatives.
- Titles are interpolated into YAML and JavaScript with limited escaping.
  Check output for quotes/apostrophes and missing coordinates.

## Working guidance

- Edit sources, not `_site/`. Keep generated content consistent when the
  corresponding source changes.
- Use a Jekyll build for template/config/content changes, then inspect the
  affected homepage, post, map, feed, or AMP output as appropriate.
- No dedicated automated test suite was identified during this inspection.
- Keep credentials and service configuration values out of documentation and
  logs; refer to their owning files or GitHub secret names instead.
- This context was inspected on 2026-11-12 against the README, source,
  templates, and checked-in workflows. A build was not run for this
  documentation-only task. Recheck mutable deployment details when needed.
