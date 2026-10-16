import os
from PIL import Image
import argparse

# --- CONFIGURATION ---
TARGET_DIR = "../_src/assets/img"
MAX_WIDTH = 1280
WEBP_QUALITY = 65


def process_image_to_webp(image_path, output_dir):
    """Converts an image to WebP, resizes if width > 1280px, and saves it."""
    # Ensure the target directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        with Image.open(image_path) as img:
            # Get original dimensions
            orig_width, orig_height = img.size

            # Resize if the image exceeds the maximum width
            if orig_width > MAX_WIDTH:
                # Calculate new height to preserve aspect ratio
                ratio = MAX_WIDTH / float(orig_width)
                new_height = int(float(orig_height) * float(ratio))
                
                # Resize the image using a high-quality resampling filter
                img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
                print(f"Resized: {orig_width}x{orig_height} -> {MAX_WIDTH}x{new_height}")
            else:
                print(f"Kept original size: {orig_width}x{orig_height}")

            # Prepare the output filename
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_filename = f"{base_name}.webp"
            output_path = os.path.join(output_dir, output_filename)

            # Save as WebP
            img.save(output_path, "WEBP", quality=WEBP_QUALITY)
            print(f"Successfully saved to: {output_path}\n")

    except Exception as e:
        print(f"Error processing {image_path}: {e}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file path.")
    parser.add_argument("filepath", type=str, help="Path to the file")
    args = parser.parse_args()

    # Example usage: Pass the path to the source image here
    source_image = args.filepath
    
    if os.path.exists(source_image):
        process_image_to_webp(source_image, TARGET_DIR)
    else:
        print(f"Source image not found: {source_image}")
