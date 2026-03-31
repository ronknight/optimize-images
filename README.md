<h1 align="center">🖼️ <a href="https://github.com/ronknight/optimize-images">Optimize Images</a></h1>
<h4 align="center">📸 A Python-based tool for compressing images efficiently using the TinyPNG API and Pillow library.</h4>

<p align="center">
<a href="https://twitter.com/PinoyITSolution"><img src="https://img.shields.io/twitter/follow/PinoyITSolution?style=social"></a>
<a href="https://github.com/ronknight?tab=followers"><img src="https://img.shields.io/github/followers/ronknight?style=social"></a>
<a href="https://github.com/ronknight/optimize-images/stargazers"><img src="https://img.shields.io/github/stars/BEPb/BEPb.svg?logo=github"></a>
<a href="https://github.com/ronknight/optimize-images/network/members"><img src="https://img.shields.io/github/forks/BEPb/BEPb.svg?color=blue&logo=github"></a>
<a href="https://youtube.com/@PinoyITSolution"><img src="https://img.shields.io/youtube/channel/subscribers/UCeoETAlg3skyMcQPqr97omg"></a>
<a href="https://github.com/ronknight/optimize-images/issues"><img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"></a>
<a href="https://github.com/ronknight/optimize-images/blob/master/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
<a href="https://github.com/ronknight"><img src="https://img.shields.io/badge/Made%20with%20%F0%9F%A4%8D%20by%20-%20Ronknight%20-%20red"></a>
</p>

<p align="center">
  <a href="#project-overview">Project Overview</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

---

## 📝 Project Overview
The **Optimize Images** project is a Python-based CLI tool for compressing image files while preserving quality. It utilizes the [TinyPNG API](https://tinypng.com/) for high-quality lossy compression and the [Pillow](https://pillow.readthedocs.io/en/stable/) library for additional preprocessing. This tool supports multiple image formats (PNG, JPEG, WebP, etc.), ensuring reduced file sizes while maintaining visual fidelity.

---

## ✨ Features
- **Multiple Format Support**: Compresses `.png`, `.jpg`, `.jpeg`, and `.webp` image formats.
- **In-Memory Precompression**: Uses Pillow for initial lossless compression before sending data to TinyPNG API.
- **Recursive Folder Processing**: Processes all images within a folder, preserving the directory structure in the output folder.
- **TinyPNG API Integration**: Ensures high-quality lossy compression for reduced image sizes.
- **WebP Conversion**: Advanced WebP converter with intelligent size detection from filenames.
- **SVG to PNG Conversion**: Converts `.svg` assets to `.png` while preserving folder structure.
- **Automatic Resize**: Resizes images while maintaining aspect ratio and centering.
- **Error Handling**: Robust error management for account issues, API limits, and network problems.

---

## 🚀 Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/ronknight/optimize-images.git
   cd optimize-images
   ```

2. **Set up the environment**:
   - Install the required Python dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Create a `.env` file in the root directory and add your TinyPNG API key:
     ```env
     TINIFY_API_KEY=your_tinify_api_key
     ```

3. **Prepare input and output folders**:
   - Ensure you have a folder containing the images you want to compress (`input_folder`).
   - Create an empty folder for the compressed images (`output_folder`).

---

## 🎯 Usage

### Main Compression Tool
Run the script to compress your images:
```bash
python optimize_images.py
```

#### CLI Workflow:
1. The script will prompt you for the input folder path:
   ```
   Enter the input folder path:
   ```
2. Provide the path to the folder containing the images you wish to compress.
3. Next, it will prompt for the output folder path:
   ```
   Enter the output folder path:
   ```
4. The script will then compress all valid images and save the compressed versions to the specified output folder, preserving the folder structure.

### WebP Converter
Convert images to WebP format with intelligent size detection:

```bash
python webp_converter.py input_folder output_folder [size] [-q quality] [-k]
```

#### WebP Converter Arguments:
- `input_folder`: Path to folder containing images to convert
- `output_folder`: Path where converted WebP images will be saved
- `size` (optional): Default target size in format `WIDTHxHEIGHT` (e.g., `800x600`) or `WIDTH` for square (e.g., `800`)
- `-q, --quality`: WebP quality from 1-100 (default: 80)
- `-k, --keep-size`: Keep original image dimensions (no resizing)

#### Smart Size Detection:
The WebP converter can automatically detect target sizes from filenames:
- `image_800x600.png` → Resizes to 800x600 pixels
- `photo_400.jpg` → Resizes to 400x400 pixels (square)
- `banner-1920x1080.webp` → Resizes to 1920x1080 pixels

#### Examples:
```bash
# Convert with automatic size detection from filenames
python webp_converter.py ./input ./output

# Convert keeping original dimensions
python webp_converter.py ./input ./output -k

# Convert with default size for files without size in filename
python webp_converter.py ./input ./output 800x600

# Convert with custom quality
python webp_converter.py ./input ./output 1024 -q 90

# Convert to square format with high quality and keep original dimensions
python webp_converter.py ./input ./output 512 --quality 95

# Keep original size with high quality
python webp_converter.py ./input ./output --keep-size --quality 95
```

### SVG to PNG Converter
Convert SVG files to PNG while preserving the input folder structure:

```bash
python svg_to_png_converter.py input_folder output_folder [--width PIXELS] [--height PIXELS] [--scale FACTOR] [--background COLOR]
```

#### SVG to PNG Converter Arguments:
- `input_folder`: Path to folder containing SVG files
- `output_folder`: Path where converted PNG files will be saved
- `--width`: Optional output width in pixels
- `--height`: Optional output height in pixels
- `--scale`: Optional scale factor for rendering (default: `1.0`)
- `--background`: Optional background color such as `white` or `#ffffff`

The converter uses `magick` from ImageMagick when it is available on your system. If ImageMagick is not installed, it falls back to `cairosvg` when that package and its native Cairo runtime are available.

#### Examples:
```bash
# Convert all SVG files using their intrinsic document size
python svg_to_png_converter.py ./logo ./optimize-logo

# Render larger PNGs with a 2x scale factor
python svg_to_png_converter.py ./logo ./optimize-logo --scale 2

# Force a specific output size
python svg_to_png_converter.py ./logo ./optimize-logo --width 1200 --height 400

# Render onto a solid white background
python svg_to_png_converter.py ./logo ./optimize-logo --background white
```

---

## 🛠️ How It Works

### Main Compression Tool:
1. **Image File Validation**:
   - The script checks file extensions (`.png`, `.jpg`, `.jpeg`, `.webp`) to determine if a file is an image.
2. **In-Memory Compression**:
   - Images are precompressed in memory using Pillow to reduce the size before sending them to the TinyPNG API.
3. **TinyPNG Compression**:
   - TinyPNG performs high-quality lossy compression to further optimize image sizes.
4. **Output Handling**:
   - Compressed images are saved in the specified output folder, retaining the original folder structure.

### WebP Converter:
1. **Format Detection**:
   - Supports multiple input formats: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`, `.tiff`.
2. **Intelligent Size Extraction**:
   - Automatically detects target dimensions from filename patterns (e.g., `image_800x600.png`).
   - Falls back to default size if no dimensions found in filename.
3. **Smart Resizing**:
   - Maintains aspect ratio during resize using high-quality Lanczos resampling.
   - Centers resized image within target dimensions.
   - Handles transparency (RGBA) and fills background appropriately.
4. **WebP Optimization**:
   - Converts to efficient WebP format with configurable quality settings.
   - Uses method 6 for optimal compression/quality balance.
5. **Logging**:
   - Tracks compression statistics and file size savings.
   - Logs errors for problematic files.

### SVG to PNG Converter:
1. **SVG Discovery**:
   - Recursively finds `.svg` files in the input folder.
2. **Raster Rendering**:
   - Uses CairoSVG to render vector assets into `.png` files.
3. **Optional Output Controls**:
   - Supports explicit width/height, render scale, and background color.
4. **Output Handling**:
   - Writes `.png` files to the output folder while preserving subdirectories.

---

## 📂 Folder Structure
```
optimize-images/
│
├── .env                      # Environment variables (TinyPNG API key)
├── app.py                    # Main application script
├── main.py                   # Entry point
├── process.py                # Image processing logic
├── webp_converter.py         # WebP conversion tool with smart sizing
├── resize_and_optimize.py    # Image resize and optimization utilities
├── log_handler.py            # Compression logging system
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── logs/                     # Compression logs directory
├── original/                 # Input images folder
└── optimized/                # Output images folder
```

---

## 🤝 Contributing
Contributions are welcome! If you'd like to improve this project:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add some feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.

---

## ⚖️ License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/ronknight/optimize-images/blob/master/LICENSE) file for details.

---

## 📜 Disclaimer
This tool relies on the TinyPNG API, which requires a valid API key for use. Ensure you have a valid account and adhere to API usage limits. Always test the tool on sample files before applying it to important images.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/ronknight">Ronknight</a>
</p>
