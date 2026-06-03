"""011 蝴蝶飞舞悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_BUTTERFLIES = 18
BUTTERFLY_COLORS = [
    (200, 150, 255),  # 淡紫
    (150, 200, 255),  # 天蓝
    (255, 180, 220),  # 粉
    (180, 255, 220),  # 薄荷
    (255, 220, 150),  # 暖黄
    (255, 160, 200),  # 玫瑰
    (180, 220, 255),  # 淡蓝
    (255, 200, 180),  # 蜜桃
]


class Butterfly:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        self.x = random.uniform(100, self.w - 100)
        self.y = random.uniform(100, self.h - 100)
        self.target_x = random.uniform(100, self.w - 100)
        self.target_y = random.uniform(100, self.h - 100)
        self.size = random.uniform(12, 28)
        self.speed = random.uniform(0.5, 1.5)
        self.color1 = random.choice(BUTTERFLY_COLORS)
        self.color2 = random.choice(BUTTERFLY_COLORS)
        self.wing_phase = random.uniform(0, math.pi * 2)
        self.wing_speed = random.uniform(0.15, 0.25)
        self.rotation = 0
        self.alpha = random.randint(180, 255)
        self.trail = []
        self.move_timer = 0
        self.move_interval = random.randint(60, 180)

    def update(self):
        # 翅膀扇动
        self.wing_phase += self.wing_speed

        # 飞向目标
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 5:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.rotation = math.atan2(dy, dx)
        else:
            self._pick_target()

        # 随机改变目标
        self.move_timer += 1
        if self.move_timer > self.move_interval:
            self._pick_target()
            self.move_timer = 0

        # 轨迹
        self.trail.append((self.x, self.y, self.wing_phase))
        if len(self.trail) > 20:
            self.trail.pop(0)

    def _pick_target(self):
        self.target_x = random.uniform(80, self.w - 80)
        self.target_y = random.uniform(80, self.h - 80)
        self.move_interval = random.randint(60, 180)

    def draw(self, painter):
        wing = math.sin(self.wing_phase)  # -1 ~ 1

        # 轨迹（发光粒子）
        for i, (tx, ty, _) in enumerate(self.trail):
            t = i / len(self.trail) if self.trail else 0
            alpha = int(60 * t)
            s = 2 * t
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(*self.color1, alpha))
            painter.drawEllipse(int(tx - s), int(ty - s), int(s * 2), int(s * 2))

        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(math.degrees(self.rotation))

        s = self.size
        wing_scale = 0.3 + 0.7 * abs(wing)  # 翅膀开合

        # 左翅
        painter.save()
        painter.scale(1, wing_scale if wing > 0 else 0.3)
        self._draw_wing(painter, -s, 0, s, self.color1, -1)
        painter.restore()

        # 右翅
        painter.save()
        painter.scale(1, wing_scale if wing < 0 else 0.3)
        self._draw_wing(painter, s, 0, s, self.color2, 1)
        painter.restore()

        # 身体
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(60, 40, 30, self.alpha))
        painter.drawEllipse(int(-2), int(-s * 0.4), 4, int(s * 0.8))

        # 触角
        painter.setPen(QPen(QColor(60, 40, 30, self.alpha), 1))
        painter.drawLine(0, int(-s * 0.3), int(-s * 0.4), int(-s * 0.8))
        painter.drawLine(0, int(-s * 0.3), int(s * 0.4), int(-s * 0.8))
        # 触角末端小点
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(60, 40, 30, self.alpha))
        painter.drawEllipse(int(-s * 0.4 - 2), int(-s * 0.8 - 2), 4, 4)
        painter.drawEllipse(int(s * 0.4 - 2), int(-s * 0.8 - 2), 4, 4)

        painter.restore()

    def _draw_wing(self, painter, cx, cy, size, color, direction):
        path = QPainterPath()
        s = size * 0.8
        # 上翅
        path.moveTo(0, 0)
        path.cubicTo(cx * 0.5, -s * 0.8, cx * 1.2, -s * 0.4, cx * 0.8, s * 0.1)
        path.cubicTo(cx * 0.4, s * 0.3, 0, s * 0.2, 0, 0)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*color, self.alpha))
        painter.drawPath(path)

        # 翅膀花纹
        path2 = QPainterPath()
        path2.addEllipse(int(cx * 0.4), int(-s * 0.2), int(s * 0.3), int(s * 0.3))
        painter.setBrush(QColor(255, 255, 255, self.alpha // 3))
        painter.drawPath(path2)


class ButterfliesOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="Butterflies")
        self.butterflies = [Butterfly(self.W, self.H) for _ in range(NUM_BUTTERFLIES)]

    def on_regenerate(self):
        for b in self.butterflies:
            b.reset()

    def update_scene(self):
        for b in self.butterflies:
            b.update()

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 15))
        for b in self.butterflies:
            b.draw(painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ButterfliesOverlay()
    win.show()
    sys.exit(app.exec())
