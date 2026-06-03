"""006 玫瑰花瓣雨悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QRadialGradient
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_PETALS = 100
PETAL_COLORS = [
    (255, 105, 180),
    (255, 140, 170),
    (255, 180, 200),
    (255, 120, 160),
    (255, 200, 210),
    (220, 80, 140),
    (255, 160, 190),
    (255, 90, 130),
    (255, 220, 230),
    (255, 150, 180),
]


class Petal:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        self.x = random.uniform(-80, self.w + 80)
        self.y = random.uniform(-150, -10)
        self.size = random.uniform(5, 22)
        self.vy = random.uniform(0.5, 2.5)
        self.vx = random.uniform(-0.5, 0.5)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-4, 4)
        self.flip_phase = random.uniform(0, math.pi * 2)
        self.flip_speed = random.uniform(0.03, 0.1)
        self.sway = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.01, 0.04)
        self.sway_amp = random.uniform(0.5, 3)
        self.color = random.choice(PETAL_COLORS)
        self.alpha = random.randint(140, 255)
        # 发光
        self.glow = random.random() < 0.3

    def update(self):
        self.y += self.vy
        self.sway += self.sway_speed
        self.x += self.vx + math.sin(self.sway) * self.sway_amp
        self.flip_phase += self.flip_speed
        self.rotation += self.rot_speed + math.sin(self.flip_phase) * 2
        if self.y > self.h + 60:
            self.reset()

    def draw(self, painter):
        flip = 0.5 + 0.5 * math.sin(self.flip_phase)
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rotation)

        s = self.size
        sx = 0.3 + 0.7 * abs(flip - 0.5) * 2
        painter.scale(sx, 1)

        path = QPainterPath()
        path.moveTo(0, -s)
        path.cubicTo(s * 0.8, -s * 0.5, s * 0.6, s * 0.5, 0, s * 0.8)
        path.cubicTo(-s * 0.6, s * 0.5, -s * 0.8, -s * 0.5, 0, -s)

        # 发光花瓣
        if self.glow:
            grad = QRadialGradient(0, 0, s * 2)
            grad.setColorAt(0, QColor(*self.color, self.alpha // 3))
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawEllipse(int(-s * 2), int(-s * 2), int(s * 4), int(s * 4))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*self.color, self.alpha))
        painter.drawPath(path)

        painter.setBrush(QColor(255, 200, 210, self.alpha // 4))
        painter.drawEllipse(int(-s * 0.15), int(-s * 0.15), int(s * 0.3), int(s * 0.3))

        painter.restore()


class RosePetalsOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="RosePetals")
        self.petals = [Petal(self.W, self.H) for _ in range(NUM_PETALS)]

    def on_regenerate(self):
        for p in self.petals:
            p.reset()

    def update_scene(self):
        for p in self.petals:
            p.update()

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 15))
        for p in self.petals:
            p.draw(painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RosePetalsOverlay()
    win.show()
    sys.exit(app.exec())
