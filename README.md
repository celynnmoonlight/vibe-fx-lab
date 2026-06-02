# Vibe FX Lab

A collection of local desktop overlay visual effects. Generate stunning animations directly on your desktop — no browser, no traditional GUI windows.

> [中文文档](README.zh.md)

## Features

- Runs entirely offline, no cloud services needed
- No browser, no traditional GUI windows
- Desktop overlay: frameless, transparent background, always on top
- Click-through support
- Default layout: 1080×1920 vertical (portrait) for short videos
- Frame sequence export + ffmpeg MP4 encoding

## Quick Start

```bash
# Install dependencies
uv sync
```

### Run Projects

```bash
# 001 Neon Particle Network
uv run projects/001_neon_particle_overlay/main.py

# 002 Geometry Tunnel
uv run projects/002_geometry_tunnel_overlay/main.py

# 003 Liquid Neon Text
uv run projects/003_liquid_neon_text_overlay/main.py

# 004 Audio Reactive Spectrum
uv run projects/004_audio_reactive_overlay/main.py
```

## Keyboard Shortcuts (All Projects)

| Key   | Action                  |
| ----- | ----------------------- |
| Esc   | Quit                    |
| R     | Start / Stop recording  |
| S     | Screenshot              |
| F     | Toggle fullscreen       |
| T     | Toggle click-through    |
| Space | Regenerate              |

## Projects

| #   | Name                    | Description                                         |
| --- | ----------------------- | --------------------------------------------------- |
| 001 | Neon Particle Network   | Particles form glowing connection networks          |
| 002 | Geometry Tunnel         | Rotating geometric shapes with depth perspective    |
| 003 | Liquid Neon Text        | Text with liquid flow trails and drip effects       |
| 004 | Audio Reactive Spectrum | Audio frequency visualization (mic or simulated)    |

## Export Video

```bash
python scripts/frames_to_video.py exports/001_neon output.mp4
```

## Tech Stack

- Python 3.11+
- PyQt6
- NumPy
- Pillow
- ffmpeg (external)
