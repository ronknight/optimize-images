"""Destination-based formats and the complete local conversion pipeline."""

import os
from pathlib import Path
import sys
from unittest.mock import Mock

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
pytest.importorskip('tinify')
os.environ.setdefault('TINIFY_API_KEY', 'test-key-not-used')

import app  # noqa: E402


@pytest.mark.parametrize(('name', 'expected'), [
    ('Black-Friday-1600x500L.png', 'webp'),
    ('Black-Friday-500x500L.png', 'webp'),
    ('Black-Friday-900x525L.png', 'webp'),
    ('Black-Friday-900x525E.webp', 'png'),
    ('black-friday-900X525e.png', 'png'),
    ('Black-Friday-900x525.png', 'png'),
    ('Toys-Black-Friday-1320x350.png', 'png'),
    ('category-520x400.webp', 'png'),
    ('banner-1600x500.png', 'webp'),
    ('banner-1920x500.png', 'webp'),
    ('unlabeled-500x500.png', 'png'),
    ('2026-10-16-banner-900x525.png', 'png'),
    ('2026-10-16-banner-1920x500.png', 'webp'),
    ('email/banner-1920x500L.png', 'png'),
    ('landing-page/banner-900x525.png', 'webp'),
    ('tablet/banner-900x525.png', 'webp'),
    ('web/banner-900x525E.png', 'png'),
    (r'C:\banners\email\banner-1600x500.png', 'png'),
    ('animated.gif', 'gif'),
])
def test_format_follows_destination_before_dimensions(name: str, expected: str) -> None:
    assert app.select_output_format(name)[0] == expected


@pytest.mark.parametrize(('size', 'expected'), [
    ((1920, 500), 'webp'), ((900, 525), 'png'), ((317, 119), 'png'),
])
def test_unlabeled_image_uses_pixels_then_compatibility_fallback(
    tmp_path: Path, size: tuple[int, int], expected: str,
) -> None:
    source = tmp_path / 'artwork.png'
    Image.new('RGB', size, 'blue').save(source)
    assert app.select_output_format(source)[0] == expected


def install_local_tinify(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Replace only the remote step; decode and inspect real Pillow outputs."""
    def from_buffer(data: bytes) -> Mock:
        return Mock(to_file=lambda path: Path(path).write_bytes(data))

    remote = Mock(side_effect=from_buffer)
    monkeypatch.setattr(app.tinify, 'from_buffer', remote)
    monkeypatch.setattr(app, 'logger', Mock())
    app.logger.log_compression.return_value = {
        'savings': 0, 'original_size': 1, 'compressed_size': 1,
    }
    return remote


def test_mixed_batch_writes_matching_extensions_bytes_and_subdirectories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / 'original'
    source.mkdir()
    (source / 'nested').mkdir()
    Image.new('RGBA', (32, 32), (50, 70, 90, 128)).save(source / 'hero-900x525E.png')
    Image.new('RGB', (40, 40), 'blue').save(source / 'nested' / 'hero-900x525L.png')
    remote = install_local_tinify(monkeypatch)
    output = tmp_path / 'optimized'

    assert app.compress_images(source, output, target_size=(32, 32),
                               convert_to='auto', trim=False) == (2, 2)
    with Image.open(output / 'hero-900x525E.png') as email:
        assert (email.format, email.size) == ('PNG', (32, 32))
        assert email.getpixel((16, 16))[3] == 128
    with Image.open(output / 'nested' / 'hero-900x525L.webp') as web:
        assert (web.format, web.size) == ('WEBP', (32, 32))
    assert remote.call_count == 2


@pytest.mark.parametrize(('convert_to', 'expected'), [
    (None, 'PNG'), ('png', 'PNG'), ('webp', 'WEBP'),
])
def test_existing_explicit_and_preserve_modes_bypass_auto(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    convert_to: str | None, expected: str,
) -> None:
    source = tmp_path / 'original'
    source.mkdir()
    Image.new('RGB', (20, 20), 'blue').save(source / 'hero-900x525E.png')
    install_local_tinify(monkeypatch)
    selector = Mock(side_effect=AssertionError('Auto selection must be opt-in'))
    monkeypatch.setattr(app, 'select_output_format', selector)
    output = tmp_path / 'optimized'

    assert app.compress_images(source, output, convert_to=convert_to,
                               target_size=(20, 20)) == (1, 1)
    with Image.open(next(output.iterdir())) as result:
        assert result.format == expected
    selector.assert_not_called()


def test_auto_gif_keeps_frames_and_skips_tinify(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / 'original'
    source.mkdir()
    Image.new('RGB', (20, 20), 'red').save(
        source / 'animated.gif', save_all=True,
        append_images=[Image.new('RGB', (20, 20), 'blue')], duration=100, loop=0,
    )
    remote = install_local_tinify(monkeypatch)
    output = tmp_path / 'optimized'
    assert app.compress_images(source, output, convert_to='auto', trim=False) == (1, 1)
    with Image.open(output / 'animated.gif') as result:
        assert result.format == 'GIF'
        assert result.n_frames == 2
    remote.assert_not_called()


def test_cli_dry_run_needs_no_key_and_writes_no_images(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture,
) -> None:
    source = tmp_path / 'original'
    source.mkdir()
    Image.new('RGB', (20, 20), 'blue').save(source / 'hero-900x525E.png')
    output = tmp_path / 'not-created'
    remote = install_local_tinify(monkeypatch)
    monkeypatch.setattr(app, 'TINIFY_API_KEY', None)
    monkeypatch.setattr(sys, 'argv', ['app.py', '--convert-to', 'auto', '--dry-run',
                                     str(source), str(output)])

    app.main()

    assert not output.exists()
    remote.assert_not_called()
    printed = capsys.readouterr().out
    assert 'Auto format: PNG' in printed
    assert 'hero-900x525E.png' in printed
    assert 'Planned images: 1' in printed


def test_dates_do_not_hide_dimensions() -> None:
    assert app.parse_dimensions_from_text('2026-10-16') is None
    assert app.parse_dimensions_from_text('2026-10-16-banner-900x525E.png') == (900, 525)
    assert app.parse_dimensions_from_text('banner-1320_350.png') == (1320, 350)


def test_missing_unlabeled_image_raises_specific_error() -> None:
    with pytest.raises(FileNotFoundError):
        app.select_output_format('missing-unlabeled-image.png')
