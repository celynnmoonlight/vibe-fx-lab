"""009 樱花飘落悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QBrush
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_PETALS = 60
SAKURA_COLORS = [
    (255, 183, 197),
    (255, 192, 203),
    (255, 218, 225),
    (255, 200, 215),
    (255, 170, 190),
    (255, 228, 236),
    (248, 180, 200),
    (255, 210, 220),
]


class SakuraPetal:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        self.x = random.uniform(-80, self.w + 80)
        self.y = random.uniform(-120, -20)
        self.size = random.uniform(6, 16)
        self.vy = random.uniform(0.6, 1.8)
        self.vx = random.uniform(-0.8, 0.3)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2, 2)
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.015, 0.04)
        self.sway_amp = random.uniform(1.0, 3.0)
        self.flip_phase = random.uniform(0, math.pi * 2)
        self.flip_speed = random.uniform(0.03, 0.08)
        self.color = random.choice(SAKURA_COLORS)
        self.alpha = random.randint(180, 255)

    def update(self):
        self.y += self.vy
        self.sway_phase += self.sway_speed
        self.x += self.vx + math.sin(self.sway_phase) * self.sway_amp
        self.rotation += self.rot_speed
        self.flip_phase += self.flip_speed
        if self.y > self.h + 60:
            self.reset()

    def draw(self, painter):
        flip = 0.5 + 0.5 * math.sin(self.flip_phase)  # 0~1 模拟翻转
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rotation)

        s = self.size
        # X 方向缩放模拟 3D 翻转
        sx = 0.3 + 0.7 * abs(flip - 0.5) * 2
        painter.scale(sx, 1)

        # 花瓣形状
        path = QPainterPath()
        path.moveTo(0, -s)
        path.cubicTo(s * 0.7, -s * 0.6, s * 0.5, s * 0.3, 0, s * 0.7)
        path.cubicTo(-s * 0.5, s * 0.3, -s * 0.7, -s * 0.6, 0, -s)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*self.color, self.alpha))
        painter.drawPath(path)

        # 花瓣中心淡淡的颜色
        painter.setBrush(QColor(255, 150, 180, self.alpha // 3))
        painter.drawEllipse(int(-s * 0.2), int(-s * 0.2), int(s * 0.4), int(s * 0.4))

        painter.restore()


class CherryBlossomsOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="CherryBlossoms")
        self.petals = [SakuraPetal(self.W, self.H) for _ in range(NUM_PETALS)]

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
    win = CherryBlossomsOverlay()
    win.show()
    sys.exit(app.exec())
