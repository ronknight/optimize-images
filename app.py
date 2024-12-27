import os
import io
import tinify
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the TinyPNG API key from environment variables
TINIFY_API_KEY = os.getenv("TINIFY_API_KEY")

if not TINIFY_API_KEY:
    raise ValueError("Error: TINIFY_API_KEY is not set in the environment variables.")

# Set the API key for tinify
tinify.key = TINIFY_API_KEY
def is_image_file(filename):
    """
    Check if a file is an image based on its extension.
    Feel free to expand this list to include other formats.
    """
    valid_extensions = [".png", ".jpg", ".jpeg", ".webp"]
    ext = os.path.splitext(filename)[1].lower()
    return ext in valid_extensions

def lossless_compress_in_memory(src_path):
    """
    Open the image with Pillow, do (mostly) lossless compression in memory,
    and return the resulting bytes. This helps reduce file size before
    sending to Tinify.
    """
    # Read the image
    with Image.open(src_path) as img:
        # Pillow identifies format from the file itself, 
        # which can differ from the extension in rare cases.
        img_format = img.format

        # Prepare an in-memory buffer
        buffer = io.BytesIO()

        # For JPEG, we can minimize quality loss by using quality=100 + optimize
        # For PNG, we can use optimize=True which is lossless
        # For other formats, just save them in their original format if possible
        if img_format == "JPEG":
            img.save(buffer, format="JPEG", quality=100, optimize=True)
        elif img_format == "PNG":
            # Pillow's "optimize=True" for PNG is typically lossless
            img.save(buffer, format="PNG", optimize=True)
        elif img_format == "WEBP":
            # If you want to keep WebP, Pillow can do lossless webp
            # "lossless=True" is possible from Pillow 9.0 onwards
            # fallback to a good default if older Pillow version
            try:
                img.save(buffer, format="WEBP", lossless=True, quality=100, method=6)
            except TypeError:
                # For older Pillow versions, just do the default
                img.save(buffer, format="WEBP", quality=100, method=6)
        else:
            # If it's some other format, attempt saving in the same format
            # or default to PNG as a fallback
            try:
                img.save(buffer, format=img_format)
            except ValueError:
                # If Pillow doesn't support the original format for saving,
                # fallback to PNG
                img.save(buffer, format="PNG", optimize=True)

        # Get the compressed bytes
        return buffer.getvalue()

def compress_images(input_folder, output_folder):
    """
    Recursively find and compress images from input_folder,
    then save them to output_folder, preserving subdirectories.
    """
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if is_image_file(file):
                # Build the full source (input) path
                src_path = os.path.join(root, file)

                # Calculate the relative path to preserve the folder structure
                relative_path = os.path.relpath(src_path, input_folder)

                # Create the corresponding subfolder under output_folder
                dest_path = os.path.join(output_folder, relative_path)
                dest_dir = os.path.dirname(dest_path)
                os.makedirs(dest_dir, exist_ok=True)

                print(f"Compressing: {src_path} -> {dest_path}")

                try:
                    # 1) First do a lossless in-memory compression
                    precompressed_data = lossless_compress_in_memory(src_path)

                    # 2) Then pass that data to Tinify
                    source = tinify.from_buffer(precompressed_data)
                    source.to_file(dest_path)

                except tinify.errors.AccountError as e:
                    print(f"Account Error: {e.message}")
                    print("Verify your API key and account limits.")
                except tinify.errors.ClientError as e:
                    print(f"Client Error: {e.message}")
                    print("Check source image and request options.")
                except tinify.errors.ServerError as e:
                    print(f"Server Error: {e.message}")
                    print("Temporary issue with the Tinify API.")
                except tinify.errors.ConnectionError as e:
                    print(f"Connection Error: {e.message}")
                    print("A network connection error occurred.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

def main():
    # Prompt for input and output folder paths
    input_folder = input("Enter the input folder path: ").strip()
    output_folder = input("Enter the output folder path: ").strip()

    # Validate input folder
    if not os.path.isdir(input_folder):
        print("Error: The specified input folder does not exist.")
        return

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Start compression
    compress_images(input_folder, output_folder)
    print("Image compression process completed.")

if __name__ == "__main__":
    main()
