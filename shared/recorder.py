"""帧录制器"""

import os
import time
from PIL import Image


class FrameRecorder:
    def __init__(self, output_dir="exports", prefix="frame"):
        self.output_dir = output_dir
        self.prefix = prefix
        self.recording = False
        self.frames = []
        self.frame_index = 0
        self.session_dir = None

    def start(self):
        os.makedirs(self.output_dir, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(self.output_dir, f"{self.prefix}_{ts}")
        os.makedirs(self.session_dir, exist_ok=True)
        self.recording = True
        self.frame_index = 0
        self.frames.clear()
        print(f"[录制] 开始 → {self.session_dir}")

    def stop(self):
        self.recording = False
        print(f"[录制] 停止，共 {self.frame_index} 帧")

    def toggle(self):
        if self.recording:
            self.stop()
        else:
            self.start()

    def capture(self, qimage):
        """保存一帧 QImage"""
        if not self.recording:
            return
        # QImage → PIL Image
        w, h = qimage.width(), qimage.height()
        ptr = qimage.bits()
        ptr.setsize(h * qimage.bytesPerLine())
        arr = bytes(ptr)
        img = Image.frombuffer("RGBA", (w, h), arr, "raw", "BGRA", qimage.bytesPerLine(), 1)
        path = os.path.join(self.session_dir, f"{self.prefix}_{self.frame_index:06d}.png")
        img.save(path)
        self.frame_index += 1

    def screenshot(self, qimage, name=None):
        """单张截图"""
        os.makedirs(self.output_dir, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        fname = name or f"screenshot_{ts}.png"
        path = os.path.join(self.output_dir, fname)
        w, h = qimage.width(), qimage.height()
        ptr = qimage.bits()
        ptr.setsize(h * qimage.bytesPerLine())
        arr = bytes(ptr)
        img = Image.frombuffer("RGBA", (w, h), arr, "raw", "BGRA", qimage.bytesPerLine(), 1)
        img.save(path)
        print(f"[截图] {path}")
