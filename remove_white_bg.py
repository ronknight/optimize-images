import os
import subprocess

# Paths
IMAGEMAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
INPUT_DIR = 'input'
OUTPUT_DIR = 'optimized'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Process each image file in input directory
for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(('.gif', '.png')):
        input_path = os.path.join(INPUT_DIR, filename)
        file_ext = os.path.splitext(filename)[1].lower()
        output_filename = os.path.splitext(filename)[0] + '_transparent' + file_ext
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        print(f"Processing: {input_path}")
        cmd = [
            IMAGEMAGICK_PATH,
            input_path,
            '-transparent', 'white',
            '-trim', '+repage',
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  → Saved to: {output_path}")
        else:
            print(f"  → Error: {result.stderr}")

print("Done processing images.")
