# Changelog

## [Unreleased]

### Added

#### 2026-10-21 - Keep social-media (SM) images as PNG in auto mode

- `app.py`: `select_output_format` returns PNG for an `SM` suffix right after
  dimensions (e.g. `940x788SM`) or a `social`/`social-media` label, ranked with
  email markers so a web label or desktop slot cannot turn it into WebP.
- `tests/test_format_selection.py`: cover SM suffix, lowercase, web-folder
  precedence, and the folder label.
- `README.md`: add the SM row to the format table and update the flowchart.

### Fixed

#### 2026-10-20 - Honor --width without --height

- `app.py`: `--width` alone was dropped with "Both --width and --height must be
  specified together. Ignoring size settings." It now scales each image
  proportionally to that width (new `scale_to_width`, upscale capped by
  `--max-upscale`), overriding subfolder/filename sizes. `--height` alone still
  warns and is ignored.
- `tests/test_format_selection.py`: cover width-only scaling, the upscale cap,
  and the CLI no longer ignoring `--width`.
- `README.md`: document width-only resizing.

### Added

#### 2026-10-16 - Select banner formats by Marketing Command Center destination

- `app.py`: add `--convert-to auto`. Email markers and shared email slots use
  PNG; landing-page markers (`L` suffix included) and desktop web slots use
  WebP. Unknown destinations use PNG, and GIF inputs keep the GIF pipeline.
- `app.py`: add `--dry-run` to preview output paths, dimensions, and selection
  reasons without image writes, TinyPNG requests, or an API key. Explicit format
  overrides and source-format preservation retain their existing behavior.
- `app.py`: ignore dates without discarding dimensions elsewhere in filenames.
- `tests/test_format_selection.py`: cover destination precedence, actual Pillow
  output formats, subdirectories, alpha retention, GIF frames, format overrides,
  and key-free CLI previews. `pyproject.toml` limits test discovery to `tests/`
  so archived source snapshots are not collected.
- `README.md`: document the rules, Black Friday command, and decision diagram.
  `.gitignore` excludes local source restore points under `archive/`.
