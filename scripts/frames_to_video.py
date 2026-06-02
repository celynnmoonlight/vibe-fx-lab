"""帧序列转 MP4 视频"""

import sys, os, subprocess, glob


def convert(input_dir, output_file, fps=60):
    pattern = os.path.join(input_dir, "*.png")
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"未找到帧文件: {pattern}")
        return

    print(f"找到 {len(files)} 帧，合成 {fps}fps 视频...")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(input_dir, "%06d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "18",
        output_file
    ]

    # 尝试自动检测文件名格式
    first = os.path.basename(files[0])
    if "_" in first:
        # 如 frame_000000.png
        cmd[5] = os.path.join(input_dir, first[:first.rfind('_') + 1] + "%06d.png")

    subprocess.run(cmd)
    print(f"完成: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"用法: python {sys.argv[0]} <帧目录> <输出文件> [fps]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    convert(input_dir, output_file, fps)
