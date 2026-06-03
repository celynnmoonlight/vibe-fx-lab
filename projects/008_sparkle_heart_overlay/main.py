"""008 烟花爱心悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QPainterPath
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

FIREWORK_INTERVAL = 25
PARTICLE_COUNT = 80
HEART_COUNT = 20
GRAVITY = 0.035

LOVE_COLORS = [
    (255, 105, 180),
    (255, 182, 193),
    (255, 20, 147),
    (238, 130, 238),
    (255, 160, 200),
    (255, 192, 203),
    (255, 140, 180),
    (255, 255, 200),
    (200, 220, 255),
    (255, 220, 150),
]


class FireworkParticle:
    def __init__(self, x, y, color, is_heart=False):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 6) if not is_heart else random.uniform(0.3, 3.5)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - (2.5 if not is_heart else 1.5)
        self.color = color
        self.life = random.uniform(35, 90)
        self.max_life = self.life
        self.size = random.uniform(1, 4.5) if not is_heart else random.uniform(3, 8)
        self.is_heart = is_heart
        self.trail = []
        self.trail_max = 8 if is_heart else 5
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-5, 5)

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_max:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY
        self.vx *= 0.99
        self.life -= 1
        self.rotation += self.rot_speed

    @property
    def alive(self):
        return self.life > 0

    def draw(self, painter):
        ratio = self.life / self.max_life
        alpha = int(255 * ratio)

        for i, (tx, ty) in enumerate(self.trail):
            t = (i + 1) / len(self.trail) if self.trail else 0
            a = int(alpha * t * 0.4)
            s = self.size * t * 0.6
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(*self.color, a))
            painter.drawEllipse(int(tx - s), int(ty - s), int(s * 2), int(s * 2))

        if self.is_heart:
            self._draw_heart(painter, self.x, self.y, self.size * ratio, alpha)
        else:
            s = self.size * ratio
            grad = QRadialGradient(self.x, self.y, s * 3)
            grad.setColorAt(0, QColor(*self.color, alpha))
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawEllipse(int(self.x - s * 3), int(self.y - s * 3),
                                int(s * 6), int(s * 6))
            painter.setBrush(QColor(*self.color, alpha))
            painter.drawEllipse(int(self.x - s), int(self.y - s), int(s * 2), int(s * 2))

    def _draw_heart(self, painter, cx, cy, size, alpha):
        path = QPainterPath()
        s = size
        path.moveTo(cx, cy + s * 0.3)
        path.cubicTo(cx - s * 0.5, cy - s * 0.3, cx - s * 0.8, cy + s * 0.1, cx, cy + s * 0.7)
        path.moveTo(cx, cy + s * 0.3)
        path.cubicTo(cx + s * 0.5, cy - s * 0.3, cx + s * 0.8, cy + s * 0.1, cx, cy + s * 0.7)

        # 发光
        grad = QRadialGradient(cx, cy, s * 1.5)
        grad.setColorAt(0, QColor(*self.color, alpha // 2))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawEllipse(int(cx - s * 1.5), int(cy - s * 1.5), int(s * 3), int(s * 3))

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
        cx = random.uniform(self.W * 0.1, self.W * 0.9)
        cy = random.uniform(self.H * 0.1, self.H * 0.5)
        color = random.choice(LOVE_COLORS)
        # 同时爆发多组
        for _ in range(PARTICLE_COUNT):
            self.particles.append(FireworkParticle(cx, cy, color, is_heart=False))
        for _ in range(HEART_COUNT):
            self.particles.append(FireworkParticle(cx, cy, color, is_heart=True))

    def update_scene(self):
        self.timer_count += 1
        if self.timer_count % FIREWORK_INTERVAL == 0:
            self._launch()
            # 有时同时放两个
            if random.random() < 0.4:
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
