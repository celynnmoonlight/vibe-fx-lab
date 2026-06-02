"""关闭所有 VibeFX 悬浮层进程"""

import subprocess
import sys


def kill_all():
    """查找并关闭所有 vibe-fx 相关的 Python 进程"""
    titles = [
        "NeonParticleNetwork",
        "GeometryTunnel",
        "LiquidNeonText",
        "AudioReactiveSpectrum",
    ]

    killed = 0
    for title in titles:
        try:
            # 通过窗口标题查找进程
            result = subprocess.run(
                ["tasklist", "/FI", f"WINDOWTITLE eq {title}", "/FO", "CSV", "/NH"],
                capture_output=True, text=True
            )
            for line in result.stdout.strip().split("\n"):
                if "python" in line.lower():
                    pid = line.split(",")[1].strip('"')
                    subprocess.run(["taskkill", "/PID", pid, "/F"])
                    print(f"[关闭] {title} (PID: {pid})")
                    killed += 1
        except Exception:
            pass

    if killed == 0:
        print("没有找到运行中的 VibeFX 进程")
    else:
        print(f"共关闭 {killed} 个进程")


if __name__ == "__main__":
    kill_all()
