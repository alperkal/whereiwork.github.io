# whereiwork.github.io

A Jekyll-based photo blog deployed to GitHub Pages. Each post is a title, a location, and a photo — no text.

## Adding new posts

### Option A: Python script (recommended)

The Python script replaces all the shell scripts with a single command. It resizes the image, extracts EXIF date and GPS coordinates, creates post files, generates responsive images, updates the map data, and creates AMP stories.

#### Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Usage

```bash
# Activate the venv (if not already active)
source venv/bin/activate

# With explicit image and title
python new_post.py assets/img/kinderhotel1.jpg "Donnersbachwald - Austria"

# Auto-detect from last git commit (image + commit message)
python new_post.py
```

### Option B: Shell scripts

The original shell scripts require `exiftool`, `imagemagick`, `jpegoptim`, and `optipng` to be installed.

On macOS:

```bash
brew install exiftool imagemagick jpegoptim optipng
```

**`newPost.sh`** — Main entry point. Resizes the image, extracts EXIF data, creates the post and AMP markdown files, then calls the other scripts.

```bash
./newPost.sh <path-to-image> <title>
./newPost.sh assets/img/kinderhotel1.jpg "Donnersbachwald - Austria"
```

**`gitcheck.sh`** — Auto-detects the image and title from the last git commit and calls `newPost.sh`. Useful for CI or automation.

```bash
./gitcheck.sh
```

**`bash-responsive-images.sh`** — Generates optimised responsive copies (320, 640, 960, 1280, 1600px wide) of all images into `assets/img/optimised/`.

**`processMap.sh`** — Reads all posts and generates `assets/js/nodes.js` with location data for the map, and creates AMP stories in `_stories/`.

**`createStories.sh`** — Generates the AMP story file (`_stories/main.md`) from the most recent posts.

## Local development

```bash
gem install bundler
bundle install
bundle exec jekyll serve
```

Then open `http://localhost:4000`.

## RSS feed

The RSS feed is available at `/rss-feed.xml` and includes image previews for each post.
