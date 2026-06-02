"""004 音乐响应频谱悬浮层"""

import sys, os, math, random, struct, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QRadialGradient
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow
from shared.colors import random_neon

# 尝试导入音频库
try:
    import pyaudio
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False

NUM_BARS = 64
BAR_SMOOTHING = 0.15
PEAK_FALL = 0.3
GLOW_LAYERS = 3


class AudioSpectrumOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="AudioReactiveSpectrum")
        self.bars = np.zeros(NUM_BARS)
        self.peaks = np.zeros(NUM_BARS)
        self.bar_targets = np.zeros(NUM_BARS)
        self.colors = [random_neon() for _ in range(NUM_BARS)]
        self.time = 0
        self.audio_stream = None
        self.simulated = True

        if HAS_AUDIO:
            self._init_audio()
        else:
            print("[音频] pyaudio 未安装，使用模拟模式")

    def _init_audio(self):
        try:
            pa = pyaudio.PyAudio()
            self.audio_stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=2048
            )
            self.simulated = False
            print("[音频] 已连接麦克风")
        except Exception as e:
            print(f"[音频] 无法打开麦克风: {e}，使用模拟模式")

    def on_regenerate(self):
        self.colors = [random_neon() for _ in range(NUM_BARS)]

    def update_scene(self):
        self.time += 0.02

        if self.simulated:
            self._simulate_audio()
        else:
            self._read_audio()

        # 平滑
        self.bars += (self.bar_targets - self.bars) * BAR_SMOOTHING

        # 峰值衰减
        for i in range(NUM_BARS):
            if self.bars[i] > self.peaks[i]:
                self.peaks[i] = self.bars[i]
            else:
                self.peaks[i] -= PEAK_FALL

    def _simulate_audio(self):
        for i in range(NUM_BARS):
            base = math.sin(self.time * 2 + i * 0.3) * 0.3 + 0.3
            pulse = math.sin(self.time * 5 + i * 0.1) * 0.2
            noise = random.uniform(-0.1, 0.1)
            bass_boost = max(0, 1 - i / 10) * 0.3 * (0.5 + 0.5 * math.sin(self.time * 3))
            self.bar_targets[i] = max(0, min(1, base + pulse + noise + bass_boost))

    def _read_audio(self):
        try:
            data = self.audio_stream.read(2048, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            samples /= 32768.0
            fft = np.abs(np.fft.rfft(samples))
            fft = fft[:NUM_BARS * 4]
            # 分组取平均
            chunk = len(fft) // NUM_BARS
            for i in range(NUM_BARS):
                start = i * chunk
                end = start + chunk
                self.bar_targets[i] = min(1.0, np.mean(fft[start:end]) * 5)
        except Exception:
            pass

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 20))

        bar_w = self.W / NUM_BARS
        max_h = self.H * 0.7

        for i in range(NUM_BARS):
            h = max_h * self.bars[i]
            x = i * bar_w
            y = self.H - h
            color = self.colors[i]

            # 多层发光
            for g in range(GLOW_LAYERS, 0, -1):
                spread = g * 8
                alpha = int(40 / g)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(*color, alpha))
                painter.drawRoundedRect(
                    int(x - spread), int(y - spread),
                    int(bar_w + spread * 2), int(h + spread * 2),
                    4, 4
                )

            # 主柱
            grad = QLinearGradient(x, y, x, self.H)
            grad.setColorAt(0, QColor(*color, 255))
            grad.setColorAt(0.5, QColor(*color, 180))
            grad.setColorAt(1, QColor(*color, 40))
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(int(x + 2), int(y), int(bar_w - 4), int(h), 3, 3)

            # 峰值线
            peak_y = self.H - max_h * self.peaks[i]
            painter.setPen(QPen(QColor(*color, 200), 2))
            painter.drawLine(int(x + 2), int(peak_y), int(x + bar_w - 2), int(peak_y))

        # 中央脉冲圆
        avg = np.mean(self.bars)
        pulse_r = 60 + avg * 200
        grad = QRadialGradient(self.W / 2, self.H / 2, pulse_r)
        c = self.colors[0]
        grad.setColorAt(0, QColor(*c, int(60 * avg)))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawEllipse(
            int(self.W / 2 - pulse_r), int(self.H / 2 - pulse_r),
            int(pulse_r * 2), int(pulse_r * 2)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AudioSpectrumOverlay()
    win.show()
    sys.exit(app.exec())
