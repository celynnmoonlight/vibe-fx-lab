"""006 玫瑰花瓣雨悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_PETALS = 50
PETAL_COLORS = [
    (255, 105, 180),
    (255, 140, 170),
    (255, 180, 200),
    (255, 120, 160),
    (255, 200, 210),
    (220, 80, 140),
    (255, 160, 190),
    (255, 90, 130),
]


class Petal:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        self.x = random.uniform(-50, self.w + 50)
        self.y = random.uniform(-100, -20)
        self.size = random.uniform(8, 20)
        self.vy = random.uniform(0.8, 2.0)
        self.vx = random.uniform(-0.3, 0.3)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-3, 3)
        self.wobble = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.02, 0.06)
        self.wobble_amp = random.uniform(1, 3)
        self.color = random.choice(PETAL_COLORS)
        self.alpha = random.randint(160, 255)
        self.sway = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.01, 0.03)

    def update(self):
        self.y += self.vy
        self.sway += self.sway_speed
        self.x += self.vx + math.sin(self.sway) * 0.5
        self.wobble += self.wobble_speed
        self.rotation += self.rot_speed + math.sin(self.wobble) * 2
        if self.y > self.h + 50:
            self.reset()

    def draw(self, painter):
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rotation)

        s = self.size
        path = QPainterPath()
        # 花瓣形状：椭圆 + 尖端
        path.moveTo(0, -s)
        path.cubicTo(s * 0.8, -s * 0.5, s * 0.6, s * 0.5, 0, s * 0.8)
        path.cubicTo(-s * 0.6, s * 0.5, -s * 0.8, -s * 0.5, 0, -s)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*self.color, self.alpha))
        painter.drawPath(path)

        # 花瓣纹理线
        painter.setPen(QPen(QColor(255, 255, 255, self.alpha // 3), 0.5))
        painter.drawLine(0, int(-s * 0.8), 0, int(s * 0.5))

        painter.restore()


class RosePetalsOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="RosePetals")
        self.petals = [Petal(self.W, self.H) for _ in range(NUM_PETALS)]
        self.time = 0

    def on_regenerate(self):
        for p in self.petals:
            p.reset()

    def update_scene(self):
        self.time += 1
        for p in self.petals:
            p.update()

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 18))

        for p in self.petals:
            p.draw(painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RosePetalsOverlay()
    win.show()
    sys.exit(app.exec())
