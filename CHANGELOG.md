# Changelog

## [Unreleased]

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
