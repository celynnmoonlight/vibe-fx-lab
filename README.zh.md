# Vibe FX Lab

纯本地桌面悬浮视觉特效合集。用代码直接在桌面上生成酷炫动画，不需要浏览器、不需要传统 GUI 窗口。

> [English](README.md)

## 特点

- 纯本地运行，不依赖云服务
- 无浏览器、无传统 GUI 窗口
- 桌面 Overlay 悬浮层：无边框、透明背景、置顶显示
- 支持点击穿透
- 默认适配 1080×1920 竖屏短视频
- 支持帧序列导出 + ffmpeg 合成 MP4

## 快速开始

```bash
# 安装依赖
uv sync
```

### 运行项目

```bash
# 001 霓虹粒子网络悬浮层
uv run projects/001_neon_particle_overlay/main.py

# 002 几何霓虹隧道悬浮层
uv run projects/002_geometry_tunnel_overlay/main.py

# 003 液化霓虹文字悬浮层
uv run projects/003_liquid_neon_text_overlay/main.py

# 004 音乐响应频谱悬浮层
uv run projects/004_audio_reactive_overlay/main.py

# 005 飘浮爱心悬浮层
uv run projects/005_floating_hearts_overlay/main.py

# 006 玫瑰花瓣雨悬浮层
uv run projects/006_rose_petals_overlay/main.py

# 007 星空爱心连线悬浮层
uv run projects/007_starry_love_overlay/main.py

# 008 烟花爱心悬浮层
uv run projects/008_sparkle_heart_overlay/main.py
```

## 快捷键（所有项目通用）

| 键    | 功能           |
| ----- | -------------- |
| Esc   | 退出           |
| R     | 开始/停止录制  |
| S     | 截图           |
| F     | 切换全屏       |
| T     | 切换点击穿透   |
| Space | 重新随机生成   |

## 项目列表

| #   | 项目               | 说明                                  |
| --- | ------------------ | ------------------------------------- |
| 001 | 霓虹粒子网络悬浮层 | 粒子连线网络，霓虹发光效果            |
| 002 | 几何霓虹隧道悬浮层 | 旋转几何隧道，深度透视动画            |
| 003 | 液化霓虹文字悬浮层 | 文字液化流动，霓虹光效                |
| 004 | 音乐响应频谱悬浮层 | 音频频谱可视化，支持麦克风/模拟模式   |
| 005 | 飘浮爱心悬浮层     | 粉色爱心缓缓飘起，带闪光粒子          |
| 006 | 玫瑰花瓣雨悬浮层   | 玫瑰花瓣飘落旋转，浪漫氛围            |
| 007 | 星空爱心连线悬浮层 | 爱心沿爱心轨迹运动，繁星闪烁          |
| 008 | 烟花爱心悬浮层     | 粉色烟花绽放，爆炸中散落小爱心        |

## 导出视频

```bash
python scripts/frames_to_video.py exports/001_neon output.mp4
```

## 技术栈

- Python 3.11+
- PyQt6
- NumPy
- Pillow
- ffmpeg（外部工具）
