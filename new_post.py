#!/usr/bin/env python3
"""
Replaces the manual bash pipeline (newPost.sh, bash-responsive-images.sh,
processMap.sh, createStories.sh, gitcheck.sh) with a single Python script.

Usage:
    python new_post.py <image_path> <title>
    python new_post.py                        # auto-detect from last git commit

Examples:
    python new_post.py assets/img/kinderhotel1.jpg "Donnersbachwald - Austria"
    python new_post.py   # uses last git commit's file & message (like gitcheck.sh)
"""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image
import exifread


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
POSTS_DIR = BASE_DIR / "_posts"
AMP_DIR = BASE_DIR / "_amp"
STORIES_DIR = BASE_DIR / "_stories"
IMG_DIR = BASE_DIR / "assets" / "img"
OPTIMISED_DIR = IMG_DIR / "optimised"
NODES_JS = BASE_DIR / "assets" / "js" / "nodes.js"

RESPONSIVE_SIZES = [320, 640, 960, 1280, 1600]
MAX_STORY_SIZE = 10
STORY_NAME = "main"
RESIZE_HEIGHT = 1000


# ---------------------------------------------------------------------------
# EXIF helpers
# ---------------------------------------------------------------------------
def _dms_to_decimal(dms_values, ref):
    """Convert EXIF DMS (degrees, minutes, seconds) to decimal degrees."""
    d = float(dms_values[0])
    m = float(dms_values[1])
    s = float(dms_values[2])
    decimal = d + m / 60.0 + s / 3600.0
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


def get_exif_data(image_path: Path):
    """Return (date_str, latitude, longitude) from EXIF data."""
    with open(image_path, "rb") as f:
        tags = exifread.process_file(f, details=False)

    # Date
    date_tag = tags.get("EXIF DateTimeOriginal") or tags.get("Image DateTime")
    date_str = ""
    if date_tag:
        # EXIF format: "2024:03:15 10:30:00" → "2024-03-15"
        raw = str(date_tag).strip()
        date_str = raw[:10].replace(":", "-")

    # GPS
    lat = lon = ""
    lat_tag = tags.get("GPS GPSLatitude")
    lat_ref = tags.get("GPS GPSLatitudeRef")
    lon_tag = tags.get("GPS GPSLongitude")
    lon_ref = tags.get("GPS GPSLongitudeRef")

    if lat_tag and lat_ref:
        lat = _dms_to_decimal(lat_tag.values, str(lat_ref))
    if lon_tag and lon_ref:
        lon = _dms_to_decimal(lon_tag.values, str(lon_ref))

    return date_str, lat, lon


# ---------------------------------------------------------------------------
# Step 1: Resize the original image to height=1000
# ---------------------------------------------------------------------------
def resize_image(image_path: Path):
    """Resize image so its height is RESIZE_HEIGHT, preserving aspect ratio."""
    with Image.open(image_path) as img:
        if img.height <= RESIZE_HEIGHT:
            return
        ratio = RESIZE_HEIGHT / img.height
        new_width = int(img.width * ratio)
        img_resized = img.resize((new_width, RESIZE_HEIGHT), Image.LANCZOS)
        # Preserve EXIF by copying info
        exif_data = img.info.get("exif")
        if exif_data:
            img_resized.save(image_path, exif=exif_data)
        else:
            img_resized.save(image_path)
    print(f"Resized {image_path} to height {RESIZE_HEIGHT}")


# ---------------------------------------------------------------------------
# Step 2: Create post markdown files (_posts/ and _amp/)
# ---------------------------------------------------------------------------
def create_post(image_path: Path, title: str):
    """Create the Jekyll post and AMP post markdown files."""
    date_str, latitude, longitude = get_exif_data(image_path)
    name = image_path.stem  # filename without extension

    if not date_str:
        print("WARNING: No EXIF date found. Using 'UNKNOWN' as date prefix.")
        date_str = "UNKNOWN"

    # _posts/<date>-<name>.md
    post_path = POSTS_DIR / f"{date_str}-{name}.md"
    post_content = f"""---
layout: post
title: "{title}"
author: "Alper Kalaycioglu"
categories: whereiwork
tags: [documentation]
image: assets/img/{name}.jpg
amp: true
location:
  latitude: {latitude}
  longitude: {longitude}
---"""
    post_path.write_text(post_content + "\n")
    print(f"Created {post_path}")

    # _amp/<date>-<name>.md
    amp_path = AMP_DIR / f"{date_str}-{name}.md"
    amp_content = f"""---
layout: amp
title: "{title}"
author: "Alper Kalaycioglu"
categories: whereiwork
tags: [documentation]
image: {name}.jpg
location:
  latitude: {latitude}
  longitude: {longitude}
---"""
    amp_path.write_text(amp_content + "\n")
    print(f"Created {amp_path}")


# ---------------------------------------------------------------------------
# Step 3: Generate responsive images (bash-responsive-images.sh)
# ---------------------------------------------------------------------------
def generate_responsive_images():
    """Create optimised responsive copies of every image in assets/img/."""
    OPTIMISED_DIR.mkdir(parents=True, exist_ok=True)

    source_files = sorted(IMG_DIR.glob("*"))
    source_files = [
        f for f in source_files if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]

    for src in source_files:
        print(f"\nOptimising '{src}'")
        with Image.open(src) as img:
            file_width = img.width

        for size in RESPONSIVE_SIZES:
            dest_dir = OPTIMISED_DIR / str(size)
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / src.name

            if dest_file.exists():
                print(f"  {dest_file} exists, skipping...")
                continue

            if size > file_width:
                print(f"  '{src.name}' is smaller than {size}px, copying...")
                shutil.copy2(src, dest_file)
            else:
                print(f"  Creating '{dest_file}'")
                with Image.open(src) as img:
                    ratio = size / img.width
                    new_height = int(img.height * ratio)
                    resized = img.resize((size, new_height), Image.LANCZOS)
                    if src.suffix.lower() == ".png":
                        resized.save(dest_file, optimize=True)
                    else:
                        resized.save(
                            dest_file,
                            quality=85,
                            optimize=True,
                            progressive=True,
                        )

            # If compressed file is larger than original, replace with original
            if dest_file.exists() and dest_file.stat().st_size > src.stat().st_size:
                print(f"  '{dest_file}' is bigger than original, replacing with copy...")
                dest_file.unlink()
                shutil.copy2(src, dest_file)


# ---------------------------------------------------------------------------
# Step 4: Process map / generate nodes.js (processMap.sh)
# ---------------------------------------------------------------------------
def _parse_post_frontmatter(post_path: Path):
    """Extract title, latitude, longitude, and image from a post's YAML front matter."""
    content = post_path.read_text()
    title = latitude = longitude = image = ""

    for line in content.splitlines():
        if line.strip().startswith("title:"):
            # title: "Some Title"
            title = line.split(":", 1)[1].strip().strip('"')
        elif line.strip().startswith("latitude:"):
            latitude = line.split(":", 1)[1].strip()
        elif line.strip().startswith("longitude:"):
            longitude = line.split(":", 1)[1].strip()
        elif line.strip().startswith("image:"):
            image = line.split(":", 1)[1].strip()

    return title, latitude, longitude, image


def process_map():
    """Generate assets/js/nodes.js with location data from all posts."""
    print("\nProcessing maps...")
    NODES_JS.parent.mkdir(parents=True, exist_ok=True)

    posts = sorted(POSTS_DIR.glob("*.md"))
    lines = ["var locations = [\t"]

    for post in posts:
        title, lat, lon, image = _parse_post_frontmatter(post)
        # Link: strip first 11 chars of filename (date prefix "YYYY-MM-DD-") and extension
        link = post.stem[11:]  # remove "YYYY-MM-DD-" prefix
        # The bash script cuts from char 19 of the full path "_posts/YYYY-MM-DD-..."
        # which effectively gives the slug after the date
        lines.append(f"['{title}', {lat}, {lon}, '{image}', '/{post.stem}'],")

    lines.append("];")
    NODES_JS.write_text("\n".join(lines) + "\n")
    print(f"Generated {NODES_JS}")


# ---------------------------------------------------------------------------
# Step 5: Create AMP stories (createStories.sh)
# ---------------------------------------------------------------------------
def create_stories():
    """Generate _stories/main.md AMP story from posts."""
    print("\nProcessing Stories...")
    STORIES_DIR.mkdir(parents=True, exist_ok=True)
    story_path = STORIES_DIR / f"{STORY_NAME}.md"

    posts = sorted(POSTS_DIR.glob("*.md"))
    if not posts:
        print("No posts found, skipping story generation.")
        return

    # Cover = last post (most recent by filename sort)
    cover_post = posts[-1]
    cover_title, _, _, cover_image = _parse_post_frontmatter(cover_post)
    # Extract just the filename from image path like "assets/img/foo.jpg" → "foo.jpg"
    cover_image_name = Path(cover_image).name if cover_image else ""

    lines = [
        "---",
        "layout: ampstory",
        "title: whereI.work/today",
        "cover:",
        f"  title: <h1>{cover_title}</h1>",
        f"  background: /assets/img/optimised/640/{cover_image_name}",
        "pages: ",
    ]

    counter = 0
    for post in posts:
        if post == cover_post:
            continue
        title, _, _, image = _parse_post_frontmatter(post)
        image_name = Path(image).name if image else ""
        lines.append(f"- layout: thirds")
        lines.append(f"  top: <h1>{title}</h1>")
        lines.append(f"  background: /assets/img/optimised/640/{image_name}")
        counter += 1
        if counter >= MAX_STORY_SIZE:
            break

    lines.append("---")
    story_path.write_text("\n".join(lines) + "\n")
    print(f"Generated {story_path}")


# ---------------------------------------------------------------------------
# Git-check mode (gitcheck.sh) — auto-detect from last commit
# ---------------------------------------------------------------------------
def git_auto_detect():
    """Detect the image and title from the last git commit (like gitcheck.sh)."""
    try:
        filename = (
            subprocess.check_output(
                ["git", "diff", "--name-only", "HEAD^"],
                cwd=BASE_DIR,
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
            .splitlines()[0]
        )
    except (subprocess.CalledProcessError, IndexError):
        print("Could not detect file from last git commit.")
        sys.exit(1)

    try:
        commit_msg = (
            subprocess.check_output(
                ["git", "log", "-1", "--pretty=format:%B"],
                cwd=BASE_DIR,
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        commit_msg = ""

    # Only process jpg images in assets/img/
    if filename.startswith("assets/img/") and filename.lower().endswith((".jpg", ".jpeg")):
        return filename, commit_msg
    else:
        print(f"Last commit file '{filename}' is not a jpg in assets/img/. Nothing to do.")
        sys.exit(0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Create a new Jekyll post from an image with EXIF data."
    )
    parser.add_argument("image", nargs="?", help="Path to image file (e.g. assets/img/photo.jpg)")
    parser.add_argument("title", nargs="?", help="Post title (e.g. \"Vienna - Austria\")")
    args = parser.parse_args()

    if args.image and args.title:
        image_path = BASE_DIR / args.image
        title = args.title
    elif not args.image and not args.title:
        print("No arguments provided — auto-detecting from last git commit...")
        filename, title = git_auto_detect()
        image_path = BASE_DIR / filename
    else:
        parser.error("Provide both <image> and <title>, or neither for git auto-detect.")

    if not image_path.exists():
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)

    print(f"Processing: {image_path}")
    print(f"Title: {title}\n")

    # Step 1: Resize
    resize_image(image_path)

    # Step 2: Create post files
    create_post(image_path, title)

    # Step 3: Generate responsive images
    generate_responsive_images()

    # Step 4: Process map (nodes.js)
    process_map()

    # Step 5: Create stories
    create_stories()

    print("\nDone!")


if __name__ == "__main__":
    main()
