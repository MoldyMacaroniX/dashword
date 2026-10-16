#!/usr/bin/env python3

import argparse
import base64
import io
import json
import re
import sys
import unicodedata
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

from PIL import Image


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_WIDTH = 1280
AUTHOR_MAX_WIDTH = 100
WEBP_QUALITY = 65

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

POSTS_DIR = PROJECT_ROOT / "_src" / "posts"
IMAGE_DIR = PROJECT_ROOT / "_src" / "assets" / "img"
AVATAR_DIR = PROJECT_ROOT / "_src" / "assets" / "avatars"
AUTHORS_FILE = PROJECT_ROOT / "_src" / "_data" / "authors.json"


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def error(message):
    """Print an error and exit."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def slugify(text):
    """
    Convert article title to a URL/file slug.

    Example:
        "My Amazing Article!" -> "my-amazing-article"
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def normalize_typography(text):
    """
    Convert Google's typographic punctuation to the site's preferred
    plain-text equivalents.
    """
    replacements = {
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',

        "‘": "'",
        "’": "'",
        "‚": "'",
        "‛": "'",

        "…": "...",

        "‹": "'",
        "›": "'",

        "′": "'",
        "″": '"',
    }

    # for old, new in replacements.items():
        # text = text.replace(old, new)

    return text

def generate_author_key(name):
    """
    Generate an author key by removing spaces and special characters.

    Example:
        "Jane Doe!" -> "janedoe"
    """
    normalized = unicodedata.normalize("NFKD", name)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]", "", normalized).lower()


def unique_path(directory, filename):
    """
    Return a path that doesn't already exist.

    article.webp
    article-1.webp
    article-2.webp
    etc.
    """
    directory.mkdir(parents=True, exist_ok=True)

    path = directory / filename

    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix

    number = 1

    while True:
        candidate = directory / f"{stem}-{number}{suffix}"

        if not candidate.exists():
            return candidate

        number += 1


def download_url(url):
    """
    Download a URL and return its contents as bytes.
    """
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ArticleImporter/1.0"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not download {url}: {exc}") from exc


def parse_image_url(url):
    """
    Download an image URL.

    Returns:
        bytes
    """
    if not url:
        return None

    return download_url(url)


def decode_data_url(data_url):
    """
    Decode a base64 data URL such as:

        data:image/png;base64,iVBORw0KGgo...
    """
    match = re.match(
        r"^data:image/[^;]+;base64,(.*)$",
        data_url,
        re.DOTALL | re.IGNORECASE
    )

    if not match:
        raise ValueError("Unsupported image data URL")

    try:
        return base64.b64decode(match.group(1))
    except Exception as exc:
        raise ValueError("Invalid base64 image data") from exc


def process_image(
    image_data,
    output_path,
    max_width=MAX_WIDTH,
    quality=WEBP_QUALITY
):
    """
    Open image data with Pillow, resize if necessary, and save as WebP.
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        image.load()
    except Exception as exc:
        raise RuntimeError(f"Could not read image: {exc}") from exc

    original_size = image.size

    # Convert modes that WebP doesn't handle as expected.
    if image.mode not in ("RGB", "RGBA"):
        if "transparency" in image.info:
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

    # Only shrink images; don't enlarge small images.
    if image.width > max_width:
        new_height = round(image.height * max_width / image.width)

        image = image.resize(
            (max_width, new_height),
            Image.Resampling.LANCZOS
        )

    output_size = image.size

    output_path.parent.mkdir(parents=True, exist_ok=True)

    image.save(
        output_path,
        "WEBP",
        quality=quality,
        method=6
    )

    print(
        f"    {output_path.name}: "
        f"{original_size[0]}x{original_size[1]} -> "
        f"{output_size[0]}x{output_size[1]}"
    )

    return output_path


# ---------------------------------------------------------------------------
# Metadata parsing
# ---------------------------------------------------------------------------

REQUIRED_METADATA = {
    "Title",
    "Desc",
    "Author Key",
}


def parse_metadata_and_body(content):
    """
    Parse the Google Docs metadata block.

    Google Docs exports:

        \\---
        Title: ...
        ...
        \\---

    The template itself uses normal:

        ---
        ...
        ---

    Both are supported.
    """

    lines = content.splitlines()

    # Find opening delimiter.
    if not lines:
        raise ValueError("The Markdown file is empty.")

    first_line = lines[0].strip()

    if first_line not in ("---", r"\---"):
        raise ValueError(
            "The file does not begin with a metadata block. "
            "Expected '---' or '\\---'."
        )

    # Find closing delimiter.
    closing_index = None

    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", r"\---"):
            closing_index = i
            break

    if closing_index is None:
        raise ValueError("Could not find the end of the metadata block.")

    metadata = {}

    for line in lines[1:closing_index]:
        # Google Docs Markdown export may leave two spaces at the end.
        line = line.rstrip()

        if not line:
            continue

        if ":" not in line:
            raise ValueError(
                f"Invalid metadata line:\n{line}"
            )

        key, value = line.split(":", 1)

        key = key.strip()
        value = value.strip()

        # Google Docs may export URLs as Markdown links:
        #
        # [https://example.com/image.png](https://example.com/image.png)
        #
        # Convert these back into plain URLs.
        value = extract_url(value)

        metadata[key] = value

    body = "\n".join(lines[closing_index + 1:])

    # Remove the blank line immediately following the metadata block.
    body = body.lstrip("\n")

    return metadata, body


def extract_url(value):
    """
    Convert a Google Docs Markdown link into its URL.

    Example:

        [https://example.com/foo.png](https://example.com/foo.png)

    becomes:

        https://example.com/foo.png
    """

    match = re.fullmatch(
        r"\[([^\]]+)\]\(([^)]+)\)",
        value
    )

    if match and match.group(1) == match.group(2):
        return match.group(2)

    return value


# ---------------------------------------------------------------------------
# Inline Google Docs image processing
# ---------------------------------------------------------------------------

IMAGE_REFERENCE_RE = re.compile(
    r"!\[([^\]]*)\]\[([^\]]+)\]"
)

IMAGE_DEFINITION_RE = re.compile(
    r"^\[([^\]]+)\]:\s*<?(data:image/[^>\s]+)>?\s*$",
    re.MULTILINE
)


def process_inline_images(body, slug, created_files):
    """
    Find Google Docs reference-style images and replace them with normal
    paths to processed WebP images.

    Google Docs produces something like:

        ![][image1]

    and at the bottom:

        [image1]: <data:image/png;base64,...>
    """

    definitions = {}

    for match in IMAGE_DEFINITION_RE.finditer(body):
        reference = match.group(1)
        data_url = match.group(2)
        definitions[reference] = data_url

    if not definitions:
        return body

    image_number = 0

    def replace_image(match):
        nonlocal image_number

        alt_text = match.group(1)
        reference = match.group(2)

        if reference not in definitions:
            raise ValueError(
                f"Image reference '{reference}' has no image definition."
            )

        image_number += 1

        data = decode_data_url(definitions[reference])

        filename = f"{slug}-{image_number}.webp"
        output_path = unique_path(IMAGE_DIR, filename)

        process_image(
            data,
            output_path,
            max_width=MAX_WIDTH,
            quality=WEBP_QUALITY
        )

        created_files.append(output_path)

        relative_path = (
            "/assets/img/"
            + output_path.name
        )

        return f"![{alt_text}]({relative_path})"

    # Replace image references.
    body = IMAGE_REFERENCE_RE.sub(replace_image, body)

    # Remove the base64 image definitions.
    body = IMAGE_DEFINITION_RE.sub("", body)

    # Clean up excessive trailing whitespace/newlines left by definitions.
    body = body.rstrip() + "\n"

    return body


# ---------------------------------------------------------------------------
# Author handling
# ---------------------------------------------------------------------------

def load_authors():
    if not AUTHORS_FILE.exists():
        raise RuntimeError(
            f"Authors file does not exist:\n{AUTHORS_FILE}"
        )

    try:
        with AUTHORS_FILE.open("r", encoding="utf-8") as f:
            authors = json.load(f)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Could not parse {AUTHORS_FILE}: {exc}"
        ) from exc

    if not isinstance(authors, list):
        raise RuntimeError(
            f"{AUTHORS_FILE} must contain a JSON array."
        )

    return authors


def save_authors(authors):
    """
    Write authors.json with readable indentation.
    """
    with AUTHORS_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            authors,
            f,
            indent=4,
            ensure_ascii=False
        )
        f.write("\n")


def find_author(authors, key):
    for author in authors:
        if author.get("key") == key:
            return author

    return None


def create_author(metadata, authors, created_files):
    """
    Create an author if they don't already exist.

    Existing authors are never modified.
    """

    name = metadata.get("Author Name", "").strip()

    # if not name:
    #     raise ValueError("Author Name is required.")

    key = metadata.get("Author Key", "").strip()

    if not key:
        key = generate_author_key(name)

    if not key:
        raise ValueError(
            "Could not generate an author key from the author name."
        )

    existing = find_author(authors, key)

    if existing is not None:
        print(f"Author '{key}' already exists; leaving it unchanged.")
        return key, False

    author = {
        "key": key,
        "name": name,
        "bio": metadata.get("Author Bio", ""),
        "photo": "",
        "youtube": metadata.get("Author YouTube", ""),
        "handle": True,
        "twitch": metadata.get("Author Twitch", ""),
        "twitter": metadata.get("Author Twitter", ""),
        "discord": metadata.get("Author Discord", ""),
        "gdbrowser": metadata.get("Author GDBrowser", "")
    }

    photo_url = metadata.get("Author Photo", "").strip()

    if photo_url:
        print(f"Downloading author photo...")

        image_data = parse_image_url(photo_url)

        filename = f"{key}.webp"
        output_path = unique_path(AVATAR_DIR, filename)

        process_image(
            image_data,
            output_path,
            max_width=AUTHOR_MAX_WIDTH,
            quality=WEBP_QUALITY
        )

        created_files.append(output_path)

        author["photo"] = (
            "/assets/avatars/"
            + output_path.name
        )

    authors.append(author)

    return key, True


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------

def yaml_quote(value):
    """
    Safely quote a string for YAML frontmatter.

    Double quotes are escaped.
    """
    value = str(value)
    # value = value.replace("\\", "\\\\")
    # value = value.replace('"', '\\"')
    return f'"{value}"'


def create_frontmatter(metadata, author_key, cover_path):
    title = metadata["Title"]
    desc = metadata["Desc"]

    tags = metadata.get("Tags", "")

    if tags:
        tags = [
            tag.strip()
            for tag in tags.split(",")
            if tag.strip()
        ]
    else:
        tags = []

    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        f"desc: {yaml_quote(desc)}",
        f"date: {date.today().isoformat()}",
        "tags:"
    ]

    for tag in tags:
        lines.append(f"  - {yaml_quote(tag)}")

    lines.extend([
        f"author: {yaml_quote(author_key)}",
        f"image: {yaml_quote(cover_path)}",
        f"imageSource: {yaml_quote(metadata.get('Cover Source', ''))}",
        "---",
        ""
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main import process
# ---------------------------------------------------------------------------

def import_article(input_file):
    input_file = Path(input_file).resolve()

    if not input_file.exists():
        error(f"Input file does not exist:\n{input_file}")

    if input_file.suffix.lower() != ".md":
        error("Input file must have a .md extension.")

    try:
        content = input_file.read_text(encoding="utf-8")
    except Exception as exc:
        error(f"Could not read input file: {exc}")

    # -----------------------------------------------------------------------
    # Parse metadata
    # -----------------------------------------------------------------------

    try:
        metadata, body = parse_metadata_and_body(content)
    except ValueError as exc:
        error(str(exc))

    missing = [
        key
        for key in REQUIRED_METADATA
        if not metadata.get(key, "").strip()
    ]

    if missing:
        error(
            "Missing required metadata:\n"
            + "\n".join(f"  - {key}" for key in missing)
        )

    title = metadata["Title"].strip()

    slug = slugify(title)

    if not slug:
        error("Could not generate a slug from the article title.")

    output_article = POSTS_DIR / f"{slug}.md"

    if output_article.exists():
        error(
            f"An article with this slug already exists:\n"
            f"{output_article}"
        )

    print(f"Title: {title}")
    print(f"Slug:  {slug}")
    print()

    # Keep track of files so we can clean them up if something fails.
    created_files = []

    try:
        # -------------------------------------------------------------------
        # Load authors
        # -------------------------------------------------------------------

        authors = load_authors()

        # -------------------------------------------------------------------
        # Process cover
        # -------------------------------------------------------------------

        cover_url = metadata.get("Cover", "").strip()

        if not cover_url:
            error("Cover is required.")

        print("Downloading cover image...")

        cover_data = parse_image_url(cover_url)

        cover_output = unique_path(
            IMAGE_DIR,
            f"{slug}.webp"
        )

        process_image(
            cover_data,
            cover_output,
            max_width=MAX_WIDTH,
            quality=WEBP_QUALITY
        )

        created_files.append(cover_output)

        cover_path = "/assets/img/" + cover_output.name

        # -------------------------------------------------------------------
        # Process/create author
        # -------------------------------------------------------------------

        author_key, author_created = create_author(
            metadata,
            authors,
            created_files
        )

        # -------------------------------------------------------------------
        # Process inline images
        # -------------------------------------------------------------------

        print("Processing article images...")

        body = process_inline_images(
            body,
            slug,
            created_files
        )

        body = normalize_typography(body)
        metadata = normalize_typography(metadata)

        # -------------------------------------------------------------------
        # Create final article
        # -------------------------------------------------------------------

        frontmatter = create_frontmatter(
            metadata,
            author_key,
            cover_path
        )

        final_article = frontmatter + body

        POSTS_DIR.mkdir(parents=True, exist_ok=True)

        output_article.write_text(
            final_article,
            encoding="utf-8"
        )

        created_files.append(output_article)

        # -------------------------------------------------------------------
        # Save authors.json only after everything else succeeds
        # -------------------------------------------------------------------

        if author_created:
            save_authors(authors)

        print()
        print("Import successful!")
        print()
        print(f"Article: {output_article}")

        if author_created:
            print(f"Author:  {author_key} (created)")
        else:
            print(f"Author:  {author_key} (existing)")

        print(f"Cover:   {cover_output}")

        inline_count = sum(
            1
            for path in created_files
            if path.parent == IMAGE_DIR
        ) - 1

        if inline_count:
            print(f"Inline images: {inline_count}")

    except Exception as exc:
        # Remove anything we created during the failed import.
        print()
        print(f"Import failed: {exc}", file=sys.stderr)
        print("Cleaning up created files...", file=sys.stderr)

        for path in reversed(created_files):
            try:
                if path.exists():
                    path.unlink()
            except Exception as cleanup_exc:
                print(
                    f"Warning: could not remove {path}: {cleanup_exc}",
                    file=sys.stderr
                )

        sys.exit(1)


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Import a Google Docs Markdown export into the static site."
        )
    )

    parser.add_argument(
        "file",
        help="The Markdown file exported from Google Docs."
    )

    args = parser.parse_args()

    import_article(args.file)


if __name__ == "__main__":
    main()