# Upload Articles

## Prerequisites

- Python/pip
- Run
    ```
    pip install -r requirements.txt
    ```

## Run

- From an article written using our official Google Docs template, download it as a Markdown file
- Run
    ```
    cd upload # unless you're already in this directory
    python clean.py <path_to_md_file> # this will overwrite the file so maybe save a backup
    python upload.py <path_to_cleaned_md_file>
    ```

## `image.py`

For manually compressing and uploading images to `../_src/assets/img/` - run with `image.py <path_to_image>`

## TODO

Improve clean.py and upload.py cuz i lowkey copied them from gemini and chatgpt and they barely function

The idea is to:

- Have authors write an article via our [official Google Docs template](https://www.dashword.net/template)
- Clean up the article by:
    - Replacing curly quotes with straight quotes
    - Replacing any ellipses characters with three dots
    - Fixing any weird shenanigans that Google Docs inserts (they sometimes insert backslashes where they should not be)
- Compress any images and upload them to either `_src/assets/img/` or `_src/assets/avatars/`. Max width for article images should be 1280px. Max size should be 50 KB. File format should be webp. For author avatars, max width should be 100px.
- Make sure the documentation in `_src/courses/contribute-to-dashword/template.md` is up to date

If anyone wants to take this on then hey, make a PR!