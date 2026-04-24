@echo off
setlocal enabledelayedexpansion

set "IMAGEMAGICK_PATH=C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
set "INPUT_DIR=input"
set "OUTPUT_DIR=optimized"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

for %%f in ("%INPUT_DIR%\*.gif") do (
    echo Processing: %%f
    "%IMAGEMAGICK_PATH%" "%%f" -transparent white -trim +repage "%OUTPUT_DIR%\%%~nf_transparent.gif"
)

echo Done processing GIFs from %INPUT_DIR%.