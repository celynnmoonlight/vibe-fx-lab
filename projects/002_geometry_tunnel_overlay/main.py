"""002 几何霓虹隧道悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow
from shared.colors import random_neon
from shared.math_utils import rotate_point

NUM_RINGS = 12
SIDES = 6
ROTATION_SPEED = 0.008
PULSE_SPEED = 0.02


class TunnelOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="GeometryTunnel")
        self.angle = 0
        self.pulse = 0
        self.colors = [random_neon() for _ in range(NUM_RINGS)]
        self.side_count = SIDES
        self.cx, self.cy = self.W // 2, self.H // 2

    def on_regenerate(self):
        self.colors = [random_neon() for _ in range(NUM_RINGS)]
        self.side_count = random.choice([4, 5, 6, 8])

    def update_scene(self):
        self.angle += ROTATION_SPEED
        self.pulse += PULSE_SPEED

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 20))

        painter.translate(self.cx, self.cy)

        for i in range(NUM_RINGS):
            t = i / NUM_RINGS
            scale = 0.15 + t * 0.85
            base_r = min(self.W, self.H) * 0.45 * scale
            rot = self.angle * (1 + i * 0.3) * (1 if i % 2 == 0 else -1)
            breathe = 1 + 0.05 * math.sin(self.pulse + i * 0.4)
            r = base_r * breathe
            alpha = int(255 * (1 - t * 0.6))

            color = self.colors[i]
            pen = QPen(QColor(*color, alpha), max(1, int(3 * (1 - t * 0.5))))
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            pts = []
            for s in range(self.side_count):
                a = rot + 2 * math.pi * s / self.side_count
                px = r * math.cos(a)
                py = r * math.sin(a)
                pts.append(QPointF(px, py))

            painter.drawPolygon(QPolygonF(pts))

        painter.resetTransform()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TunnelOverlay()
    win.show()
    sys.exit(app.exec())
