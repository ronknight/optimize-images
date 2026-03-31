import os
import argparse
from PIL import Image
from log_handler import CompressionLogger

# Initialize the compression logger
logger = CompressionLogger()

def is_image_file(filename):
    """
    Check if a file is an image based on its extension.
    """
    valid_extensions = [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff"]
    ext = os.path.splitext(filename)[1].lower()
    return ext in valid_extensions

def parse_size(size_str):
    """
    Parse size argument in format: '800x600' or '800' (for square).
    Returns: (width, height) tuple or raises ValueError
    """
    try:
        if 'x' in size_str.lower():
            parts = size_str.lower().split('x')
            width = int(parts[0].strip())
            height = int(parts[1].strip())
            return (width, height)
        else:
            # If only one value provided, treat as square
            size = int(size_str)
            return (size, size)
    except (ValueError, IndexError):
        raise ValueError(f"Invalid size format: {size_str}. Use '800x600' or '800'")

def extract_size_from_filename(filename):
    """
    Extract size from filename pattern like 'image_800x600.png' or 'image_800.png'.
    Returns: (width, height) tuple or None if no size found
    
    Patterns recognized:
    - filename_800x600.ext
    - filename_800.ext
    - filename-800x600.ext
    - filename-800.ext
    """
    import re
    
    # Remove extension
    name_without_ext = os.path.splitext(filename)[0]
    
    # Look for pattern: _800x600 or -800x600 or _800 or -800 at the end
    patterns = [
        r'[_-](\d+)x(\d+)$',  # Matches _800x600 or -800x600
        r'[_-](\d+)$'          # Matches _800 or -800
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name_without_ext)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                # WIDTHxHEIGHT format
                width = int(groups[0])
                height = int(groups[1])
                return (width, height)
            elif len(groups) == 1:
                # Square format
                size = int(groups[0])
                return (size, size)
    
    return None

def resize_and_convert_to_webp(src_path, dest_path, target_size, quality=80, keep_size=False):
    """
    Resize image to target size and convert to WebP format.
    
    Args:
        src_path: Source image path
        dest_path: Destination WebP file path
        target_size: Tuple of (width, height) or None if keep_size=True
        quality: WebP quality (1-100, default 80)
        keep_size: If True, keeps original image dimensions (no resize)
    
    Returns:
        Tuple of (original_size_bytes, compressed_size_bytes)
    """
    try:
        # Get original file size
        original_size = os.path.getsize(src_path)
        
        # Open and convert image
        with Image.open(src_path) as img:
            # Convert RGBA to RGB if necessary (WebP can handle both)
            if img.mode == 'RGBA':
                # Keep RGBA for transparency support
                pass
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            if keep_size:
                # Keep original dimensions, just convert to WebP
                final_img = img
            else:
                # Resize while maintaining aspect ratio
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
                
                # Create a new image with the exact target size
                # Fill background with white for images without alpha channel
                if img.mode == 'RGBA':
                    final_img = Image.new('RGBA', target_size, (255, 255, 255, 0))
                else:
                    final_img = Image.new('RGB', target_size, (255, 255, 255))
                
                # Calculate position to center the resized image
                x = (target_size[0] - img.size[0]) // 2
                y = (target_size[1] - img.size[1]) // 2
                final_img.paste(img, (x, y), img if img.mode == 'RGBA' else None)
            
            # Save as WebP
            final_img.save(dest_path, format='WEBP', quality=quality, method=6)
        
        # Get compressed file size
        compressed_size = os.path.getsize(dest_path)
        
        return original_size, compressed_size
        
    except Exception as e:
        raise Exception(f"Error processing {src_path}: {str(e)}")

def convert_images(input_folder, output_folder, default_size=None, quality=80, keep_size=False):
    """
    Recursively find and convert images to WebP with size from filename.
    Preserves subdirectories in output.
    
    Args:
        input_folder: Input directory path
        output_folder: Output directory path
        default_size: Default size tuple if not found in filename (optional)
        quality: WebP quality (1-100)
        keep_size: If True, keeps original image dimensions
    
    Returns:
        Tuple of (total_processed, total_successful)
    """
    total_processed = 0
    total_successful = 0
    
    print(f"Starting WebP conversion: {input_folder} → {output_folder}")
    if keep_size:
        print("Mode: Keep original dimensions")
    elif default_size:
        print(f"Default size: {default_size[0]}x{default_size[1]}")
    print(f"Quality: {quality}")
    print("-" * 70)
    
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if is_image_file(file):
                # Build the full source (input) path
                src_path = os.path.join(root, file)
                
                # Calculate the relative path to preserve the folder structure
                relative_path = os.path.relpath(src_path, input_folder)
                
                if not keep_size:
                    # Extract size from filename
                    target_size = extract_size_from_filename(file)
                    
                    if target_size is None:
                        if default_size is None:
                            print(f"⚠ {relative_path}: No size found in filename and no default specified. Skipping.")
                            continue
                        target_size = default_size
                        size_source = "default"
                    else:
                        size_source = "filename"
                else:
                    target_size = None
                    size_source = "original"
                
                # Change extension to .webp
                relative_path_webp = os.path.splitext(relative_path)[0] + '.webp'
                
                # Create the corresponding subfolder under output_folder
                dest_path = os.path.join(output_folder, relative_path_webp)
                dest_dir = os.path.dirname(dest_path)
                os.makedirs(dest_dir, exist_ok=True)
                
                if keep_size:
                    print(f"Converting: {src_path} (keeping original size)")
                else:
                    print(f"Converting: {src_path} → {target_size[0]}x{target_size[1]} ({size_source})")
                total_processed += 1
                
                try:
                    # Resize and convert to WebP
                    original_size, compressed_size = resize_and_convert_to_webp(
                        src_path, dest_path, target_size, quality, keep_size=keep_size
                    )
                    
                    # Log the successful compression
                    log_result = logger.log_compression(
                        filename=relative_path_webp,
                        original_size=original_size,
                        compressed_size=compressed_size
                    )
                    
                    # Print conversion results
                    savings_pct = log_result['savings']
                    print(f"✓ {relative_path_webp}: {log_result['original_size']:.2f}KB → {log_result['compressed_size']:.2f}KB ({savings_pct:.2f}% saved)")
                    
                    total_successful += 1
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    print(f"✗ {relative_path}: {error_msg}")
                    logger.log_error(relative_path, error_msg)
    
    print("-" * 70)
    print(f"Conversion complete: {total_successful}/{total_processed} successful")
    
    return total_processed, total_successful

def main():
    parser = argparse.ArgumentParser(
        description='Convert images to WebP format with size from filename or default size'
    )
    parser.add_argument(
        'input_folder',
        help='Input folder path containing images'
    )
    parser.add_argument(
        'output_folder',
        help='Output folder path for WebP images'
    )
    parser.add_argument(
        'size',
        nargs='?',
        default=None,
        help='Default target size in format: WIDTHxHEIGHT (e.g., 800x600) or WIDTH (for square, e.g., 800). Optional if filenames contain size.'
    )
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=80,
        help='WebP quality (1-100, default: 80)'
    )
    parser.add_argument(
        '-k', '--keep-size',
        action='store_true',
        help='Keep original image dimensions (no resize)'
    )
    
    args = parser.parse_args()
    
    # Validate input folder
    if not os.path.isdir(args.input_folder):
        print(f"Error: The specified input folder does not exist: {args.input_folder}")
        return
    
    # Check for conflicting arguments
    if args.keep_size and args.size:
        print("Error: Cannot specify both size and --keep-size options")
        return
    
    # Parse default size if provided
    default_size = None
    if args.size and not args.keep_size:
        try:
            default_size = parse_size(args.size)
        except ValueError as e:
            print(f"Error: {e}")
            return
    
    # Validate quality
    if not (1 <= args.quality <= 100):
        print("Error: Quality must be between 1 and 100")
        return
    
    # Create output folder if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)
    
    # Start conversion
    convert_images(args.input_folder, args.output_folder, default_size, args.quality, keep_size=args.keep_size)

if __name__ == "__main__":
    main()
