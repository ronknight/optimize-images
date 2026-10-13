@echo off
setlocal enabledelayedexpansion

set "IMAGEMAGICK_PATH=C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
set "INPUT_DIR=input"
set "OUTPUT_DIR=optimized"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

for %%f in ("%INPUT_DIR%\*.gif") do (
    echo Processing: %%f
    rem Only white touching the frame edge becomes transparent; white inside the artwork stays.
    "%IMAGEMAGICK_PATH%" "%%f" -bordercolor white -border 1 -alpha set -fill none -fuzz 3%% -floodfill +0+0 white -shave 1x1 -trim +repage "%OUTPUT_DIR%\%%~nf_transparent.gif"
)

echo Done processing GIFs from %INPUT_DIR%.