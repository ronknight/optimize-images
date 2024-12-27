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
Run the script to compress your images:
```bash
python optimize_images.py
```

### CLI Workflow:
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

---

## 🛠️ How It Works
1. **Image File Validation**:
   - The script checks file extensions (`.png`, `.jpg`, `.jpeg`, `.webp`) to determine if a file is an image.
2. **In-Memory Compression**:
   - Images are precompressed in memory using Pillow to reduce the size before sending them to the TinyPNG API.
3. **TinyPNG Compression**:
   - TinyPNG performs high-quality lossy compression to further optimize image sizes.
4. **Output Handling**:
   - Compressed images are saved in the specified output folder, retaining the original folder structure.

---

## 📂 Folder Structure
```
optimize-images/
│
├── .env                # Environment variables (TinyPNG API key)
├── optimize_images.py  # Main script
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
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