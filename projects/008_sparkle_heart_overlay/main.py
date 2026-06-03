"""008 烟花爱心悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

FIREWORK_INTERVAL = 40
PARTICLE_COUNT = 60
GRAVITY = 0.04

LOVE_COLORS = [
    (255, 105, 180),
    (255, 182, 193),
    (255, 20, 147),
    (238, 130, 238),
    (255, 160, 200),
    (255, 192, 203),
    (255, 140, 180),
    (255, 255, 200),  # 暖白
]


class FireworkParticle:
    def __init__(self, x, y, color, is_heart=False):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5) if not is_heart else random.uniform(0.5, 3)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - (2 if not is_heart else 1)
        self.color = color
        self.life = random.uniform(40, 90)
        self.max_life = self.life
        self.size = random.uniform(1.5, 4) if not is_heart else random.uniform(3, 7)
        self.is_heart = is_heart
        self.trail = []
        self.trail_max = 6 if is_heart else 4

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_max:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY
        self.vx *= 0.99
        self.life -= 1

    @property
    def alive(self):
        return self.life > 0

    def draw(self, painter):
        ratio = self.life / self.max_life
        alpha = int(255 * ratio)

        # 尾迹
        for i, (tx, ty) in enumerate(self.trail):
            t = (i + 1) / len(self.trail) if self.trail else 0
            a = int(alpha * t * 0.5)
            s = self.size * t * 0.8
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(*self.color, a))
            painter.drawEllipse(int(tx - s), int(ty - s), int(s * 2), int(s * 2))

        # 粒子本体
        if self.is_heart:
            self._draw_heart(painter, self.x, self.y, self.size * ratio, alpha)
        else:
            s = self.size * ratio
            # 外发光
            grad = QRadialGradient(self.x, self.y, s * 3)
            grad.setColorAt(0, QColor(*self.color, alpha // 2))
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawEllipse(int(self.x - s * 3), int(self.y - s * 3),
                                int(s * 6), int(s * 6))
            painter.setBrush(QColor(*self.color, alpha))
            painter.drawEllipse(int(self.x - s), int(self.y - s), int(s * 2), int(s * 2))

    def _draw_heart(self, painter, cx, cy, size, alpha):
        from PyQt6.QtGui import QPainterPath
        path = QPainterPath()
        s = size
        path.moveTo(cx, cy + s * 0.3)
        path.cubicTo(cx - s * 0.5, cy - s * 0.3, cx - s * 0.8, cy + s * 0.1, cx, cy + s * 0.7)
        path.moveTo(cx, cy + s * 0.3)
        path.cubicTo(cx + s * 0.5, cy - s * 0.3, cx + s * 0.8, cy + s * 0.1, cx, cy + s * 0.7)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*self.color, alpha))
        painter.drawPath(path)


class SparkleHeartOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="SparkleHeart")
        self.particles = []
        self.timer_count = 0

    def on_regenerate(self):
        self.particles.clear()

    def _launch(self):
        cx = random.uniform(self.W * 0.15, self.W * 0.85)
        cy = random.uniform(self.H * 0.15, self.H * 0.55)
        color = random.choice(LOVE_COLORS)

        # 普通粒子
        for _ in range(PARTICLE_COUNT):
            self.particles.append(FireworkParticle(cx, cy, color, is_heart=False))

        # 爱心粒子
        for _ in range(12):
            self.particles.append(FireworkParticle(cx, cy, color, is_heart=True))

    def update_scene(self):
        self.timer_count += 1
        if self.timer_count % FIREWORK_INTERVAL == 0:
            self._launch()

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 20))

        for p in self.particles:
            p.draw(painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SparkleHeartOverlay()
    win.show()
    sys.exit(app.exec())
