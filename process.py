import os
import shutil
import re

# -----------------------------
# Configuration
# -----------------------------
SOURCE_DIR = 'output'  # Source directory containing current file structure
DEST_WALLPAPERS_DIR = os.path.join('static', 'wallpapers')  # Destination for wallpapers
DEST_THUMBNAILS_DIR = os.path.join('static', 'thumbnails')  # Destination for thumbnails

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
DEVICES = ["Laptop", "Phone", "Tablet", "Watch", "Desktop", "iPad"]
ALLOWED_EXTENSIONS = ["jpg", "png"]

# Mapping additional devices to existing ones recognized by the Flask app
DEVICE_MAPPING = {
    "iPad": "tablet",
    # "Desktop": "desktop"  # Uncomment if 'desktop' is added to the Flask app's DEVICES
}

# -----------------------------
# Helper Functions
# -----------------------------

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def rename_and_move(source_path, dest_dir, new_name):
    """Rename and move file to the destination directory."""
    create_directory(dest_dir)
    dest_path = os.path.join(dest_dir, new_name)
    try:
        shutil.move(source_path, dest_path)
        print(f"Moved: {source_path} -> {dest_path}")
    except Exception as e:
        print(f"Failed to move {source_path} to {dest_path}: {e}")

def process_wallpapers(month_path, month):
    """
    Process wallpaper images in the month's directory and its subdirectories.
    Renames them to <device>.<ext> and moves to DEST_WALLPAPERS_DIR/month/
    """
    print(f"Processing wallpapers for {month}...")
    for root, dirs, files in os.walk(month_path):
        # Determine relative path from month_path
        relative_path = os.path.relpath(root, month_path)
        
        # Skip certain subdirectories
        skip_dirs = ["Thumbnails", "TV Graphics", "Bulletin Covers", "Bulletins"]
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                # Extract device and extension
                match = re.match(r'(?i)(' + '|'.join(DEVICES) + r')\b', file)
                if match:
                    original_device = match.group(1)
                    # Map device if necessary
                    device = DEVICE_MAPPING.get(original_device, original_device).lower()
                    _, ext = os.path.splitext(file)
                    ext = ext.lower().strip('.')
                    if ext in ALLOWED_EXTENSIONS:
                        # Check if device is recognized by the Flask app
                        if device not in ["laptop", "phone", "tablet", "watch"]:
                            print(f"Skipping unrecognized device '{original_device}' in file: {file_path}")
                            continue
                        new_name = f"{device}.{ext}"
                        dest_dir = os.path.join(DEST_WALLPAPERS_DIR, month)
                        rename_and_move(file_path, dest_dir, new_name)
                else:
                    print(f"Skipped (no device match): {file_path}")

def process_thumbnails(month_path, month):
    """
    Process all 'Thumbnails' directories within the month's directory and its subdirectories.
    Renames them to <device>.<ext> and moves to DEST_THUMBNAILS_DIR/month/
    """
    print(f"Processing thumbnails for {month}...")
    for root, dirs, files in os.walk(month_path):
        # Check if current directory is 'Thumbnails'
        if os.path.basename(root).lower() == 'thumbnails':
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    # Extract device and extension
                    match = re.match(r'(?i)(' + '|'.join(DEVICES) + r')\b', file)
                    if match:
                        original_device = match.group(1)
                        # Map device if necessary
                        device = DEVICE_MAPPING.get(original_device, original_device).lower()
                        _, ext = os.path.splitext(file)
                        ext = ext.lower().strip('.')
                        if ext in ALLOWED_EXTENSIONS:
                            # Check if device is recognized by the Flask app
                            if device not in ["laptop", "phone", "tablet", "watch"]:
                                print(f"Skipping unrecognized device '{original_device}' in thumbnail: {file_path}")
                                continue
                            new_name = f"{device}.{ext}"
                            dest_dir = os.path.join(DEST_THUMBNAILS_DIR, month)
                            rename_and_move(file_path, dest_dir, new_name)
                    else:
                        print(f"Skipped thumbnail (no device match): {file_path}")

def main():
    # Iterate through each month in the source directory
    for month in MONTHS:
        month_path = os.path.join(SOURCE_DIR, month)
        if not os.path.isdir(month_path):
            print(f"Month directory not found: {month_path}. Skipping.")
            continue

        print(f"\n=== Processing Month: {month} ===")

        # Process wallpapers
        process_wallpapers(month_path, month)

        # Process thumbnails
        process_thumbnails(month_path, month)

    print("\nProcessing completed.")

if __name__ == '__main__':
    main()
