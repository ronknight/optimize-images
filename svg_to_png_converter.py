import argparse
import os
import shutil
import subprocess

from log_handler import CompressionLogger

logger = CompressionLogger()


def is_svg_file(filename):
    return os.path.splitext(filename)[1].lower() == ".svg"


def get_magick_binary():
    configured_path = os.getenv("MAGICK_BINARY")
    if configured_path and os.path.isfile(configured_path):
        return configured_path
    return shutil.which("magick")


def get_cairosvg_module():
    try:
        import cairosvg
    except (ImportError, OSError):
        return None
    return cairosvg


def build_magick_command(src_path, dest_path, width=None, height=None, scale=1.0, background=None):
    magick_binary = get_magick_binary()
    if not magick_binary:
        return None

    command = [magick_binary]

    if scale != 1.0 and width is None and height is None:
        density = max(1, round(96 * scale))
        command.extend(["-density", str(density)])

    command.append(src_path)
    command.extend(["-background", background or "none"])

    if width is not None or height is not None:
        if width is not None and height is not None:
            resize_value = f"{width}x{height}!"
        elif width is not None:
            resize_value = f"{width}x"
        else:
            resize_value = f"x{height}"
        command.extend(["-resize", resize_value])

    command.append(dest_path)
    return command


def convert_svg_to_png(src_path, dest_path, width=None, height=None, scale=1.0, background=None):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    original_size = os.path.getsize(src_path)

    magick_command = build_magick_command(
        src_path, dest_path, width=width, height=height, scale=scale, background=background
    )
    if magick_command:
        subprocess.run(magick_command, check=True, capture_output=True, text=True)
    else:
        cairosvg = get_cairosvg_module()
        if cairosvg is None:
            raise RuntimeError(
                "No SVG renderer available. Install ImageMagick and ensure `magick` is on PATH, "
                "or install cairosvg with native Cairo libraries."
            )

        cairosvg.svg2png(
            url=src_path,
            write_to=dest_path,
            output_width=width,
            output_height=height,
            scale=scale,
            background_color=background,
        )

    converted_size = os.path.getsize(dest_path)
    return original_size, converted_size


def convert_svgs(input_folder, output_folder, width=None, height=None, scale=1.0, background=None):
    total_processed = 0
    total_successful = 0

    print(f"Starting SVG to PNG conversion: {input_folder} -> {output_folder}")
    if width or height:
        print(f"Output size override: width={width or 'auto'}, height={height or 'auto'}")
    print(f"Scale: {scale}")
    if background:
        print(f"Background: {background}")
    print("-" * 70)

    for root, _, files in os.walk(input_folder):
        for file in files:
            if not is_svg_file(file):
                continue

            src_path = os.path.join(root, file)
            relative_path = os.path.relpath(src_path, input_folder)
            relative_png_path = os.path.splitext(relative_path)[0] + ".png"
            dest_path = os.path.join(output_folder, relative_png_path)

            print(f"Converting: {src_path}")
            total_processed += 1

            try:
                original_size, converted_size = convert_svg_to_png(
                    src_path,
                    dest_path,
                    width=width,
                    height=height,
                    scale=scale,
                    background=background,
                )
                log_result = logger.log_compression(
                    filename=relative_png_path,
                    original_size=original_size,
                    compressed_size=converted_size,
                    status="Converted",
                )
                print(
                    f"[OK] {relative_png_path}: "
                    f"{log_result['original_size']:.2f}KB -> {log_result['compressed_size']:.2f}KB"
                )
                total_successful += 1
            except Exception as exc:
                error_msg = str(exc)
                print(f"[ERROR] {relative_path}: {error_msg}")
                logger.log_error(relative_path, error_msg)

    print("-" * 70)
    print(f"Conversion complete: {total_successful}/{total_processed} successful")
    return total_processed, total_successful


def main():
    parser = argparse.ArgumentParser(
        description="Convert SVG files in a folder to PNG while preserving subdirectories."
    )
    parser.add_argument("input_folder", help="Input folder path containing SVG files")
    parser.add_argument("output_folder", help="Output folder path for PNG files")
    parser.add_argument("--width", type=int, default=None, help="Override output width in pixels")
    parser.add_argument("--height", type=int, default=None, help="Override output height in pixels")
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Scale factor applied when width/height are not provided (default: 1.0)",
    )
    parser.add_argument(
        "--background",
        default=None,
        help="Background color such as white, #ffffff, or rgba(255,255,255,1)",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.input_folder):
        print(f"Error: The specified input folder does not exist: {args.input_folder}")
        return

    if args.width is not None and args.width <= 0:
        print("Error: --width must be greater than 0")
        return

    if args.height is not None and args.height <= 0:
        print("Error: --height must be greater than 0")
        return

    if args.scale <= 0:
        print("Error: --scale must be greater than 0")
        return

    os.makedirs(args.output_folder, exist_ok=True)
    convert_svgs(
        args.input_folder,
        args.output_folder,
        width=args.width,
        height=args.height,
        scale=args.scale,
        background=args.background,
    )


if __name__ == "__main__":
    main()
