import os
import io
import re
import argparse
import tinify
from PIL import Image
from dotenv import load_dotenv
from log_handler import CompressionLogger

# Load environment variables from .env file
load_dotenv()

# Retrieve the TinyPNG API key from environment variables
TINIFY_API_KEY = os.getenv("TINIFY_API_KEY")

if not TINIFY_API_KEY:
    raise ValueError("Error: TINIFY_API_KEY is not set in the environment variables.")

# Set the API key for tinify
tinify.key = TINIFY_API_KEY

# Initialize the compression logger
logger = CompressionLogger()

def parse_dimensions_from_text(text):
    """
    Extract dimensions from text (filename or folder name). Supports multiple formats:
    - image_800x600.png
    - photo-1920x1080.jpg
    - file.800-600.png
    - image_800_600.jpg
    - img(800x600).png
    - img[800x600].png
    - 1518x1518 (folder names)
    - 400x400 (folder names)
    
    Returns: tuple (width, height) or None if no dimensions found
    """
    # Remove file extension to avoid issues
    text_clean = os.path.splitext(text)[0]
    
    # Pattern to match dimension formats: WIDTHxHEIGHT or WIDTH-HEIGHT or WIDTH_HEIGHT
    # Supports delimiters: x, X, -, _, within various contexts
    patterns = [
        r'^(\d{2,5})[xX\-_](\d{2,5})$',                        # Exact match for folder names like "1518x1518"
        r'[_\-\.\(\[\s](\d{2,5})[xX\-_](\d{2,5})[_\)\]\s]?',  # 800x600, 800-600, 800_600, etc.
        r'[_\-\.\(\[\s](\d{2,5})[xX\-_](\d{2,5})(?:\D|$)',     # At end or followed by non-digit
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_clean)
        if match:
            try:
                width = int(match.group(1))
                height = int(match.group(2))
                # Validate dimensions are reasonable (between 1 and 16000 pixels)
                if 1 <= width <= 16000 and 1 <= height <= 16000:
                    return (width, height)
            except (ValueError, AttributeError):
                continue
    
    return None

def parse_dimensions_from_filename(filename):
    """
    Extract dimensions from filename. Wrapper for backward compatibility.
    
    Returns: tuple (width, height) or None if no dimensions found
    """
    return parse_dimensions_from_text(filename)

def parse_dimensions_from_folder_path(folder_path):
    """
    Extract dimensions from folder path by checking each folder level.
    Looks for patterns like "1518x1518" or "400x400" in folder names.
    
    Args:
        folder_path: Full path to check for dimension patterns
        
    Returns: tuple (width, height) or None if no dimensions found
    """
    # Split path into components and check each one
    path_parts = os.path.normpath(folder_path).split(os.sep)
    
    # Check from most specific (deepest) to least specific
    for part in reversed(path_parts):
        if part:  # Skip empty parts
            dimensions = parse_dimensions_from_text(part)
            if dimensions:
                return dimensions
    
    return None

def is_image_file(filename):
    """
    Check if a file is an image based on its extension.
    Feel free to expand this list to include other formats.
    """
    valid_extensions = [".png", ".jpg", ".jpeg", ".webp", ".gif"]
    ext = os.path.splitext(filename)[1].lower()
    return ext in valid_extensions

def lossless_compress_in_memory(src_path, target_dimensions=None, target_dpi=None):
    """
    Open the image with Pillow, optionally resize based on target dimensions,
    do (mostly) lossless compression in memory, and return the resulting bytes.
    This helps reduce file size before sending to Tinify.
    
    Args:
        src_path: Path to the source image
        target_dimensions: Optional tuple (width, height) to resize image to
        target_dpi: Optional DPI value to set for the image
    """
    # Read the image
    with Image.open(src_path) as img:
        # Pillow identifies format from the file itself, 
        # which can differ from the extension in rare cases.
        img_format = img.format

        # Apply resizing if target dimensions provided
        if target_dimensions:
            target_width, target_height = target_dimensions
            # Use LANCZOS resampling for high-quality resizing
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            print(f"  Resized to: {target_width}x{target_height}")
        
        # Set DPI if specified
        if target_dpi:
            print(f"  Setting DPI to: {target_dpi}")

        # Prepare an in-memory buffer
        buffer = io.BytesIO()

        # Special handling for GIF files to preserve animation
        if img_format == "GIF" and 'duration' in img.info:
            # Save all frames for animated GIFs
            frames = []
            try:
                while True:
                    frames.append(img.copy())
                    img.seek(img.tell() + 1)
            except EOFError:
                pass
            
            # Reset position
            img.seek(0)
            
            # Save the animated GIF with optimization
            frames[0].save(
                buffer,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                optimize=True,
                duration=img.info['duration'],
                loop=img.info.get('loop', 0)
            )
        elif img_format == "GIF":
            # For static GIFs, just optimize
            img.save(buffer, format="GIF", optimize=True)
        # For JPEG, we can minimize quality loss by using quality=100 + optimize
        # For PNG, we can use optimize=True which is lossless
        # For other formats, just save them in their original format if possible
        elif img_format == "JPEG":
            save_kwargs = {"format": "JPEG", "quality": 100, "optimize": True}
            if target_dpi:
                save_kwargs["dpi"] = (target_dpi, target_dpi)
            img.save(buffer, **save_kwargs)
        elif img_format == "PNG":
            # Pillow's "optimize=True" for PNG is typically lossless
            save_kwargs = {"format": "PNG", "optimize": True}
            if target_dpi:
                save_kwargs["dpi"] = (target_dpi, target_dpi)
            img.save(buffer, **save_kwargs)
        elif img_format == "WEBP":
            # If you want to keep WebP, Pillow can do lossless webp
            # "lossless=True" is possible from Pillow 9.0 onwards
            # fallback to a good default if older Pillow version
            save_kwargs = {"format": "WEBP", "quality": 100, "method": 6}
            if target_dpi:
                save_kwargs["dpi"] = (target_dpi, target_dpi)
            try:
                save_kwargs["lossless"] = True
                img.save(buffer, **save_kwargs)
            except TypeError:
                # For older Pillow versions, just do the default
                del save_kwargs["lossless"]
                img.save(buffer, **save_kwargs)
        else:
            # If it's some other format, attempt saving in the same format
            # or default to PNG as a fallback
            try:
                save_kwargs = {"format": img_format}
                if target_dpi:
                    save_kwargs["dpi"] = (target_dpi, target_dpi)
                img.save(buffer, **save_kwargs)
            except ValueError:
                # If Pillow doesn't support the original format for saving,
                # fallback to PNG
                save_kwargs = {"format": "PNG", "optimize": True}
                if target_dpi:
                    save_kwargs["dpi"] = (target_dpi, target_dpi)
                img.save(buffer, **save_kwargs)

        # Get the compressed bytes
        return buffer.getvalue()

def compress_images(input_folder, output_folder, target_size=None, target_dpi=None):
    """
    Recursively find and compress images from input_folder,
    then save them to output_folder, preserving subdirectories.
    
    Args:
        input_folder: Path to input folder containing images
        output_folder: Path to output folder for compressed images
        target_size: Optional tuple (width, height) to resize all images to
        target_dpi: Optional DPI value to set for all images
    """
    total_processed = 0
    total_successful = 0
    
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
                total_processed += 1
                
                try:
                    # Get original file size
                    original_size = os.path.getsize(src_path)
                    
                    # Determine target dimensions with priority:
                    # 1. Command line target_size (highest priority)
                    # 2. Subfolder name dimensions
                    # 3. Filename dimensions (lowest priority)
                    target_dimensions = target_size
                    dimension_source = "command line"
                    
                    if not target_dimensions:
                        # Try to get dimensions from folder path
                        folder_dimensions = parse_dimensions_from_folder_path(root)
                        if folder_dimensions:
                            target_dimensions = folder_dimensions
                            dimension_source = "subfolder"
                    
                    if not target_dimensions:
                        # Fallback to filename parsing
                        filename_dimensions = parse_dimensions_from_filename(file)
                        if filename_dimensions:
                            target_dimensions = filename_dimensions
                            dimension_source = "filename"
                    
                    if target_dimensions:
                        print(f"  Target dimensions: {target_dimensions[0]}x{target_dimensions[1]} (from {dimension_source})")
                    
                    # 1) First do a lossless in-memory compression (with optional resizing and DPI)
                    precompressed_data = lossless_compress_in_memory(src_path, target_dimensions, target_dpi)

                    # 2) Then pass that data to Tinify
                    source = tinify.from_buffer(precompressed_data)
                    source.to_file(dest_path)
                    
                    # Get compressed file size
                    compressed_size = os.path.getsize(dest_path)
                    
                    # Log the successful compression
                    log_result = logger.log_compression(
                        filename=relative_path,
                        original_size=original_size,
                        compressed_size=compressed_size
                    )
                    
                    # Print compression results
                    savings_pct = log_result['savings']
                    print(f"Compressed {relative_path}: {log_result['original_size']:.2f}KB → {log_result['compressed_size']:.2f}KB ({savings_pct:.2f}% saved)")
                    
                    total_successful += 1

                except tinify.errors.AccountError as e:
                    error_msg = f"Account Error: {e.message}"
                    print(error_msg)
                    print("Verify your API key and account limits.")
                    logger.log_error(relative_path, error_msg)
                    
                except tinify.errors.ClientError as e:
                    error_msg = f"Client Error: {e.message}"
                    print(error_msg)
                    print("Check source image and request options.")
                    logger.log_error(relative_path, error_msg)
                    
                except tinify.errors.ServerError as e:
                    error_msg = f"Server Error: {e.message}"
                    print(error_msg)
                    print("Temporary issue with the Tinify API.")
                    logger.log_error(relative_path, error_msg)
                    
                except tinify.errors.ConnectionError as e:
                    error_msg = f"Connection Error: {e.message}"
                    print(error_msg)
                    print("A network connection error occurred.")
                    logger.log_error(relative_path, error_msg)
                    
                except Exception as e:
                    error_msg = f"An unexpected error occurred: {e}"
                    print(error_msg)
                    logger.log_error(relative_path, error_msg)
    
    return total_processed, total_successful

def parse_size_argument(size_str):
    """
    Parse size argument in format "WIDTHxHEIGHT" (e.g., "800x600")
    Returns tuple (width, height) or None if invalid
    """
    if not size_str:
        return None
    
    try:
        if 'x' in size_str.lower():
            width, height = size_str.lower().split('x')
            return (int(width), int(height))
        elif '-' in size_str:
            width, height = size_str.split('-')
            return (int(width), int(height))
    except (ValueError, IndexError):
        pass
    
    print(f"Warning: Invalid size format '{size_str}'. Expected format: WIDTHxHEIGHT (e.g., 800x600)")
    return None

def main():
    parser = argparse.ArgumentParser(description='Compress and optimize images using TinyPNG API')
    parser.add_argument('input_folder', nargs='?', help='Input folder containing images to compress')
    parser.add_argument('output_folder', nargs='?', help='Output folder for compressed images')
    parser.add_argument('--size', '-s', help='Target size in format WIDTHxHEIGHT (e.g., 800x600)')
    parser.add_argument('--dpi', '-d', type=int, help='Target DPI for images (e.g., 72, 300)')
    parser.add_argument('--width', '-w', type=int, help='Target width in pixels')
    parser.add_argument('--height', type=int, help='Target height in pixels')
    
    args = parser.parse_args()
    
    # Get input and output folders
    if args.input_folder and args.output_folder:
        input_folder = args.input_folder
        output_folder = args.output_folder
    else:
        # Fallback to interactive mode if not provided
        input_folder = input("Enter the input folder path: ").strip()
        output_folder = input("Enter the output folder path: ").strip()
    
    # Validate input folder
    if not os.path.isdir(input_folder):
        print("Error: The specified input folder does not exist.")
        return
    
    # Parse size arguments
    target_size = None
    if args.size:
        target_size = parse_size_argument(args.size)
    elif args.width and args.height:
        target_size = (args.width, args.height)
    elif args.width or args.height:
        print("Warning: Both --width and --height must be specified together. Ignoring size settings.")
    
    # Validate DPI
    target_dpi = args.dpi
    if target_dpi and (target_dpi < 1 or target_dpi > 3000):
        print("Warning: DPI should be between 1 and 3000. Using default DPI.")
        target_dpi = None
    
    # Print settings
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    if target_size:
        print(f"Target size: {target_size[0]}x{target_size[1]} (command line override)")
    else:
        print("Target size: Auto-detect from subfolders/filenames")
    if target_dpi:
        print(f"Target DPI: {target_dpi}")
    print("Size detection priority: Command line > Subfolder name > Filename")
    print("-" * 50)
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Start compression
    total_processed, total_successful = compress_images(input_folder, output_folder, target_size, target_dpi)
    print("-" * 50)
    print(f"Image compression process completed.")
    print(f"Files processed: {total_processed}")
    print(f"Successfully compressed: {total_successful}")
    if total_processed > 0:
        success_rate = (total_successful / total_processed) * 100
        print(f"Success rate: {success_rate:.1f}%")

if __name__ == "__main__":
    main()
