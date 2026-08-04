"""Regression tests for border trimming and aspect-preserving resize.

Covers the 2026-08-04 bug where a full-bleed 1920x500 banner lost its top red
bar: trim_borders() sampled the red corner pixel as "background", cropped it
away, and fit_with_padding() then re-centered the shortened image on a white
canvas -- producing white bars at the top and bottom.
"""

import os
import sys

import pytest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("tinify")
os.environ.setdefault("TINIFY_API_KEY", "test-key-not-used")

from app import fit_with_padding, is_blank_border_color, trim_borders  # noqa: E402

RED = (221, 17, 0)
BLUE = (53, 74, 255)
WHITE = (255, 255, 255)


def make_banner(width: int = 1920, height: int = 500, bar: int = 11) -> Image.Image:
    """A blue banner with full-width red bars along the top and bottom edges."""
    img = Image.new("RGB", (width, height), BLUE)
    for y in list(range(bar)) + list(range(height - bar, height)):
        for x in range(width):
            img.putpixel((x, y), RED)
    return img


def make_logo_on_white(width: int = 400, height: int = 400, pad: int = 50) -> Image.Image:
    """A blue square centered on a white field -- the case trim_borders exists for."""
    img = Image.new("RGB", (width, height), WHITE)
    img.paste(Image.new("RGB", (width - 2 * pad, height - 2 * pad), BLUE), (pad, pad))
    return img


class TestIsBlankBorderColor:
    def test_white_is_blank(self):
        assert is_blank_border_color(WHITE)

    def test_near_white_is_blank(self):
        assert is_blank_border_color((245, 244, 248))

    def test_brand_red_is_not_blank(self):
        assert not is_blank_border_color(RED)

    def test_grayscale_int_supported(self):
        assert is_blank_border_color(255)
        assert not is_blank_border_color(12)

    def test_alpha_channel_ignored(self):
        assert is_blank_border_color((255, 255, 255, 0))


class TestTrimBorders:
    def test_full_bleed_banner_is_untouched(self):
        """The regression: a colored edge must not be mistaken for padding."""
        banner = make_banner()
        trimmed = trim_borders(banner)

        assert trimmed.size == (1920, 500)
        assert trimmed.getpixel((960, 0)) == RED
        assert trimmed.getpixel((960, 499)) == RED

    def test_white_border_still_trimmed(self):
        """The original feature must keep working."""
        trimmed = trim_borders(make_logo_on_white())

        assert trimmed.size == (300, 300)
        assert trimmed.getpixel((0, 0)) == BLUE

    def test_transparent_border_still_trimmed(self):
        img = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
        img.paste(Image.new("RGBA", (300, 300), BLUE + (255,)), (50, 50))

        assert trim_borders(img).size == (300, 300)


class TestFitWithPadding:
    def test_exact_size_is_not_padded(self):
        canvas = fit_with_padding(make_banner(), (1920, 500))

        assert canvas.size == (1920, 500)
        assert canvas.getpixel((960, 0)) == RED
        assert canvas.getpixel((960, 499)) == RED

    def test_short_image_is_center_padded_white(self):
        """Padding itself is correct behavior -- only the trim feeding it was wrong."""
        canvas = fit_with_padding(Image.new("RGB", (1920, 489), BLUE), (1920, 500))

        assert canvas.size == (1920, 500)
        assert canvas.getpixel((960, 0)) == WHITE
        assert canvas.getpixel((960, 250)) == BLUE

    def test_upscale_is_capped(self):
        canvas = fit_with_padding(Image.new("RGB", (100, 100), BLUE), (1000, 1000), max_upscale=2.0)

        assert canvas.size == (1000, 1000)
        # Scaled to 200x200 and centered, so the far corner stays blank.
        assert canvas.getpixel((10, 10)) == WHITE
        assert canvas.getpixel((500, 500)) == BLUE


def test_banner_survives_trim_then_fit_end_to_end():
    """The exact pipeline that broke: trim -> fit must be a no-op here."""
    result = fit_with_padding(trim_borders(make_banner()), (1920, 500))

    assert result.size == (1920, 500)
    for y in range(11):
        assert result.getpixel((960, y)) == RED, f"top row {y} lost its red bar"
    for y in range(489, 500):
        assert result.getpixel((960, y)) == RED, f"bottom row {y} lost its red bar"
