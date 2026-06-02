"""001 霓虹粒子网络悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow
from shared.colors import random_neon
from shared.math_utils import distance

NUM_PARTICLES = 120
CONNECT_DIST = 180
SPEED = 0.8
GLOW_RADIUS = 6


class NeonParticle:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        self.x = random.uniform(0, self.w)
        self.y = random.uniform(0, self.h)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * SPEED
        self.vy = math.sin(angle) * SPEED
        self.color = random_neon()
        self.size = random.uniform(2, GLOW_RADIUS)
        self.pulse = random.uniform(0, 2 * math.pi)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.pulse += 0.05
        if self.x < -20 or self.x > self.w + 20:
            self.vx *= -1
        if self.y < -20 or self.y > self.h + 20:
            self.vy *= -1


class NeonParticleOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="NeonParticleNetwork")
        self.particles = [NeonParticle(self.W, self.H) for _ in range(NUM_PARTICLES)]

    def on_regenerate(self):
        for p in self.particles:
            p.reset()

    def update_scene(self):
        for p in self.particles:
            p.update()

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 15))

        # 连线
        for i in range(len(self.particles)):
            for j in range(i + 1, len(self.particles)):
                p1, p2 = self.particles[i], self.particles[j]
                d = distance(p1.x, p1.y, p2.x, p2.y)
                if d < CONNECT_DIST:
                    alpha = int(200 * (1 - d / CONNECT_DIST))
                    r = (p1.color[0] + p2.color[0]) // 2
                    g = (p1.color[1] + p2.color[1]) // 2
                    b = (p1.color[2] + p2.color[2]) // 2
                    pen = QPen(QColor(r, g, b, alpha), 1)
                    painter.setPen(pen)
                    painter.drawLine(int(p1.x), int(p1.y), int(p2.x), int(p2.y))

        # 粒子
        for p in self.particles:
            glow = 0.6 + 0.4 * math.sin(p.pulse)
            s = p.size * glow

            # 外发光
            grad = QRadialGradient(p.x, p.y, s * 4)
            c = QColor(*p.color, int(80 * glow))
            grad.setColorAt(0, c)
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(c)
            painter.drawEllipse(int(p.x - s * 4), int(p.y - s * 4), int(s * 8), int(s * 8))

            # 核心
            painter.setBrush(QColor(*p.color, 255))
            painter.drawEllipse(int(p.x - s), int(p.y - s), int(s * 2), int(s * 2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = NeonParticleOverlay()
    win.show()
    sys.exit(app.exec())
