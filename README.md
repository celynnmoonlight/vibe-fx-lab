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

# 005 Floating Hearts
uv run projects/005_floating_hearts_overlay/main.py

# 006 Rose Petals
uv run projects/006_rose_petals_overlay/main.py

# 007 Starry Love
uv run projects/007_starry_love_overlay/main.py

# 008 Sparkle Heart
uv run projects/008_sparkle_heart_overlay/main.py

# 009 Cherry Blossoms
uv run projects/009_cherry_blossoms_overlay/main.py

# 010 Dreamy Bubbles
uv run projects/010_dreamy_bubbles_overlay/main.py

# 011 Butterflies
uv run projects/011_butterflies_overlay/main.py

# 012 Shooting Stars
uv run projects/012_shooting_stars_overlay/main.py

# 013 Aurora
uv run projects/013_aurora_overlay/main.py

# 014 Hearts Flood
uv run projects/014_hearts_flood_overlay/main.py
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
| 005 | Floating Hearts         | Pink hearts float upward with sparkle effects       |
| 006 | Rose Petals             | Rose petals falling and swirling gently             |
| 007 | Starry Love             | Hearts trace love paths across a starry sky         |
| 008 | Sparkle Heart           | Firework explosions with heart-shaped particles     |
| 009 | Cherry Blossoms         | Sakura petals falling with 3D flip effect           |
| 010 | Dreamy Bubbles          | Rainbow transparent bubbles floating upward         |
| 011 | Butterflies             | Colorful butterflies fluttering with wing animation |
| 012 | Shooting Stars          | Meteors streaking across a starry night sky         |
| 013 | Aurora                  | Dreamy northern lights flowing in the night sky     |
| 014 | Hearts Flood            | Hearts of all sizes flooding the screen with pulse and sparkle |

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
