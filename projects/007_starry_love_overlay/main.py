"""007 星空爱心连线悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QPainterPath
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_STARS = 80
LOVE_PAIRS = 5
STAR_COLORS = [
    (255, 255, 255),
    (255, 220, 255),
    (220, 220, 255),
    (255, 200, 220),
    (200, 255, 255),
]


def heart_point(t, cx, cy, s):
    """参数方程画爱心"""
    x = s * 16 * math.sin(t) ** 3
    y = -s * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
    return cx + x, cy + y


class Star:
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.size = random.uniform(0.5, 3)
        self.color = random.choice(STAR_COLORS)
        self.twinkle = random.uniform(0, math.pi * 2)
        self.twinkle_speed = random.uniform(0.03, 0.1)

    def update(self):
        self.twinkle += self.twinkle_speed

    def draw(self, painter):
        alpha = int(128 + 127 * math.sin(self.twinkle))
        s = self.size * (0.7 + 0.3 * math.sin(self.twinkle))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*self.color, alpha))
        painter.drawEllipse(int(self.x - s), int(self.y - s), int(s * 2), int(s * 2))


class LoveConnection:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.cx = w // 2
        self.cy = h // 2
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.005, 0.015)
        self.heart_size = random.uniform(15, 35)
        self.trail = []
        self.color = random.choice([
            (255, 105, 180), (255, 182, 193), (255, 20, 147),
            (238, 130, 238), (255, 160, 200),
        ])

    def update(self):
        self.angle += self.speed
        r = min(self.w, self.h) * 0.3
        # 爱心轨迹
        hx, hy = heart_point(self.angle, self.cx, self.cy, r / 16)
        self.trail.append((hx, hy))
        if len(self.trail) > 40:
            self.trail.pop(0)

    def draw(self, painter):
        if len(self.trail) < 2:
            return

        # 轨迹线
        for i in range(1, len(self.trail)):
            t = i / len(self.trail)
            alpha = int(200 * t)
            x1, y1 = self.trail[i-1]
            x2, y2 = self.trail[i]
            painter.setPen(QPen(QColor(*self.color, alpha), 2))
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # 轨迹上的小爱心
        for i in range(0, len(self.trail), 5):
            t = i / len(self.trail)
            alpha = int(180 * t)
            x, y = self.trail[i]
            s = self.heart_size * t * 0.5
            self._draw_mini_heart(painter, x, y, s, alpha)

        # 端点大爱心
        if self.trail:
            x, y = self.trail[-1]
            self._draw_mini_heart(painter, x, y, self.heart_size, 255)

    def _draw_mini_heart(self, painter, cx, cy, size, alpha):
        path = QPainterPath()
        s = size
        path.moveTo(cx, cy + s * 0.3)
        path.cubicTo(cx - s * 0.5, cy - s * 0.3, cx - s * 0.8, cy + s * 0.1, cx, cy + s * 0.7)
        path.moveTo(cx, cy + s * 0.3)
        path.cubicTo(cx + s * 0.5, cy - s * 0.3, cx + s * 0.8, cy + s * 0.1, cx, cy + s * 0.7)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*self.color, alpha))
        painter.drawPath(path)


class StarryLoveOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="StarryLove")
        self.stars = [Star(self.W, self.H) for _ in range(NUM_STARS)]
        self.connections = [LoveConnection(self.W, self.H) for _ in range(LOVE_PAIRS)]
        self.time = 0

    def on_regenerate(self):
        self.stars = [Star(self.W, self.H) for _ in range(NUM_STARS)]
        self.connections = [LoveConnection(self.W, self.H) for _ in range(LOVE_PAIRS)]

    def update_scene(self):
        self.time += 1
        for s in self.stars:
            s.update()
        for c in self.connections:
            c.update()

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(10, 5, 25, 25))

        for s in self.stars:
            s.draw(painter)

        for c in self.connections:
            c.draw(painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StarryLoveOverlay()
    win.show()
    sys.exit(app.exec())
