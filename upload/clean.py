import argparse
import sys


def clean_markdown_text(text: str) -> str:
    """Converts curly quotes, ellipses, and unescapes colons in text."""
    # 1. Convert curly double and single quotes to straight quotes
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")

    # 2. Convert ellipsis unicode characters to three standard dots
    text = text.replace("…", "...")

    # 3. Remove backslashes specifically positioned before colons and ampersands (\: -> :) because for some ungodly reason google docs will sometimes put these in URls???
    text = text.replace("\\:", ":")
    text = text.replace("\\&", "&")

    return text


def process_file(input_path: str, output_path: str = None):
    """Reads a file, applies clean-up, and saves the result."""
    try:
        # Open with utf-8 encoding to properly read Unicode characters like curly quotes/ellipses
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        cleaned_content = clean_markdown_text(content)

        # Overwrite the input file if no separate output path is provided
        target_path = output_path if output_path else input_path

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(cleaned_content)

        print(f"Successfully cleaned: {input_path} -> {target_path}")

    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean typographic artifacts from Markdown files."
    )
    parser.add_argument("input_file", help="Path to the Markdown file to fix.")
    parser.add_argument(
        "-o",
        "--output",
        help="Optional path to save a clean copy. Overwrites input if omitted.",
        default=None,
    )

    args = parser.parse_args()
    process_file(args.input_file, args.output)
