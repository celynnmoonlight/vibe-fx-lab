"""010 梦幻泡泡悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QLinearGradient
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_BUBBLES = 40


class Bubble:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        self.x = random.uniform(50, self.w - 50)
        self.y = self.h + random.uniform(0, 300)
        self.size = random.uniform(15, 60)
        self.vy = random.uniform(-1.2, -0.3)
        self.vx = random.uniform(-0.3, 0.3)
        self.wobble = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.02, 0.05)
        self.wobble_amp = random.uniform(0.5, 2.0)
        self.alpha = random.randint(60, 150)
        # 彩虹色相
        self.hue = random.uniform(0, 360)
        self.hue_speed = random.uniform(0.5, 2)
        # 高光偏移
        self.highlight_angle = random.uniform(-0.5, 0.5)

    def update(self):
        self.y += self.vy
        self.wobble += self.wobble_speed
        self.x += self.vx + math.sin(self.wobble) * self.wobble_amp
        self.hue += self.hue_speed
        if self.y < -self.size * 2:
            self.reset()

    def draw(self, painter):
        s = self.size
        cx, cy = self.x, self.y

        # HSV 转 RGB（简化版）
        h = self.hue % 360
        hi = int(h / 60) % 6
        f = h / 60 - int(h / 60)
        v, sat = 255, 0.4
        p = int(v * (1 - sat))
        q = int(v * (1 - f * sat))
        t = int(v * (1 - (1 - f) * sat))
        rgb = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
        r, g, b = rgb[hi]

        # 泡泡主体（渐变透明）
        grad = QRadialGradient(cx - s * 0.3, cy - s * 0.3, s)
        grad.setColorAt(0, QColor(255, 255, 255, self.alpha // 2))
        grad.setColorAt(0.4, QColor(r, g, b, self.alpha))
        grad.setColorAt(0.8, QColor(r, g, b, self.alpha // 2))
        grad.setColorAt(1, QColor(r, g, b, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawEllipse(int(cx - s), int(cy - s), int(s * 2), int(s * 2))

        # 泡泡轮廓
        painter.setPen(QPen(QColor(255, 255, 255, self.alpha // 2), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(int(cx - s), int(cy - s), int(s * 2), int(s * 2))

        # 高光点
        hx = cx - s * 0.35 + self.highlight_angle * s
        hy = cy - s * 0.35
        hs = s * 0.2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, self.alpha))
        painter.drawEllipse(int(hx - hs), int(hy - hs), int(hs * 2), int(hs * 2))


class DreamyBubblesOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="DreamyBubbles")
        self.bubbles = [Bubble(self.W, self.H) for _ in range(NUM_BUBBLES)]

    def on_regenerate(self):
        for b in self.bubbles:
            b.reset()

    def update_scene(self):
        for b in self.bubbles:
            b.update()

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 15))
        for b in self.bubbles:
            b.draw(painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DreamyBubblesOverlay()
    win.show()
    sys.exit(app.exec())
