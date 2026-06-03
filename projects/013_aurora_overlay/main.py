"""013 极光流动悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QPainterPath
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_BANDS = 5
NUM_POINTS = 40

AURORA_PALETTES = [
    [(0, 255, 180), (0, 200, 255), (100, 150, 255)],   # 绿蓝紫
    [(150, 100, 255), (200, 150, 255), (255, 180, 220)], # 紫粉
    [(0, 255, 200), (100, 255, 150), (200, 255, 100)],   # 绿
    [(0, 200, 255), (150, 150, 255), (255, 100, 200)],   # 蓝紫粉
]


class AuroraBand:
    def __init__(self, w, h, index, total):
        self.w, self.h = w, h
        self.index = index
        self.total = total
        self.points = []
        self.target_points = []
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.005, 0.015)
        self.palette = random.choice(AURORA_PALETTES)
        self.alpha = random.randint(30, 70)
        self.y_base = h * (0.15 + 0.5 * index / total)
        self.amplitude = random.uniform(30, 80)
        self._init_points()

    def _init_points(self):
        self.points = []
        self.target_points = []
        for i in range(NUM_POINTS):
            x = self.w * i / (NUM_POINTS - 1)
            y = self.y_base + random.uniform(-self.amplitude, self.amplitude)
            self.points.append((x, y))
            self.target_points.append((x, y))

    def update(self):
        self.phase += self.speed

        new_targets = []
        for i in range(NUM_POINTS):
            x = self.w * i / (NUM_POINTS - 1)
            y = self.y_base + math.sin(self.phase + i * 0.3) * self.amplitude \
                + math.sin(self.phase * 0.7 + i * 0.15) * self.amplitude * 0.5
            new_targets.append((x, y))

        # 平滑插值
        smoothed = []
        for i, (pt, tgt) in enumerate(zip(self.points, new_targets)):
            sx = pt[0] + (tgt[0] - pt[0]) * 0.08
            sy = pt[1] + (tgt[1] - pt[1]) * 0.08
            smoothed.append((sx, sy))
        self.points = smoothed

    def draw(self, painter):
        if len(self.points) < 2:
            return

        # 构建带状路径
        thickness = 40 + self.index * 15

        # 上边缘
        top_path = QPainterPath()
        top_path.moveTo(self.points[0][0], self.points[0][1])
        for i in range(1, len(self.points)):
            x0, y0 = self.points[i - 1]
            x1, y1 = self.points[i]
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            top_path.quadTo(x0, y0, cx, cy)
        top_path.lineTo(self.points[-1][0], self.points[-1][1])

        # 下边缘
        bottom_path = QPainterPath()
        bottom_path.moveTo(self.points[-1][0], self.points[-1][1] + thickness)
        for i in range(len(self.points) - 2, -1, -1):
            x0, y0 = self.points[i + 1]
            x1, y1 = self.points[i]
            cx = (x0 + x1) / 2
            cy = (y0 + y1 + thickness) / 2
            bottom_path.quadTo(x0, y0 + thickness, cx, cy)
        bottom_path.lineTo(self.points[0][0], self.points[0][1] + thickness)

        # 合并路径
        full_path = top_path + bottom_path

        # 渐变填充
        grad = QLinearGradient(0, self.y_base - 50, 0, self.y_base + thickness + 50)
        c = self.palette[self.index % len(self.palette)]
        grad.setColorAt(0, QColor(*c, 0))
        grad.setColorAt(0.3, QColor(*c, self.alpha))
        grad.setColorAt(0.5, QColor(*c, self.alpha + 20))
        grad.setColorAt(0.7, QColor(*c, self.alpha))
        grad.setColorAt(1, QColor(*c, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawPath(full_path)


class AuroraOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="Aurora")
        self.bands = [AuroraBand(self.W, self.H, i, NUM_BANDS) for i in range(NUM_BANDS)]
        self.stars = []
        for _ in range(100):
            self.stars.append({
                'x': random.uniform(0, self.W),
                'y': random.uniform(0, self.H * 0.6),
                'size': random.uniform(0.5, 2),
                'twinkle': random.uniform(0, math.pi * 2),
                'speed': random.uniform(0.03, 0.1),
            })

    def on_regenerate(self):
        self.bands = [AuroraBand(self.W, self.H, i, NUM_BANDS) for i in range(NUM_BANDS)]

    def update_scene(self):
        for b in self.bands:
            b.update()
        for s in self.stars:
            s['twinkle'] += s['speed']

    def draw_scene(self, painter: QPainter):
        # 深色夜空
        painter.fillRect(0, 0, self.W, self.H, QColor(5, 5, 20, 25))

        # 星星
        for s in self.stars:
            alpha = int(100 + 155 * math.sin(s['twinkle']))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, alpha))
            painter.drawEllipse(int(s['x'] - s['size']), int(s['y'] - s['size']),
                                int(s['size'] * 2), int(s['size'] * 2))

        # 极光带
        for b in self.bands:
            b.draw(painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AuroraOverlay()
    win.show()
    sys.exit(app.exec())
