"""005 飘浮爱心悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QRadialGradient
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_HEARTS = 35
PINK_COLORS = [
    (255, 105, 180),  # 热粉
    (255, 182, 193),  # 浅粉
    (255, 20, 147),   # 深粉
    (255, 160, 200),  # 玫瑰粉
    (255, 192, 203),  # 粉红
    (255, 140, 180),  # 桃粉
    (238, 130, 238),  # 紫罗兰
    (255, 100, 150),  # 草莓
]


def heart_path(cx, cy, size):
    """生成爱心形状路径"""
    path = QPainterPath()
    s = size
    path.moveTo(cx, cy + s * 0.4)
    path.cubicTo(cx - s * 0.5, cy - s * 0.2, cx - s, cy + s * 0.1, cx, cy + s * 0.8)
    path.moveTo(cx, cy + s * 0.4)
    path.cubicTo(cx + s * 0.5, cy - s * 0.2, cx + s, cy + s * 0.1, cx, cy + s * 0.8)
    return path


class Heart:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        self.x = random.uniform(50, self.w - 50)
        self.y = self.h + random.uniform(0, 200)
        self.size = random.uniform(15, 45)
        self.vy = random.uniform(-1.5, -0.5)
        self.vx = random.uniform(-0.5, 0.5)
        self.wobble = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.02, 0.05)
        self.wobble_amp = random.uniform(0.5, 2.0)
        self.rotation = random.uniform(-0.3, 0.3)
        self.rot_speed = random.uniform(-0.005, 0.005)
        self.color = random.choice(PINK_COLORS)
        self.alpha = random.randint(150, 255)
        self.pulse = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.03, 0.06)

    def update(self):
        self.y += self.vy
        self.wobble += self.wobble_speed
        self.x += self.vx + math.sin(self.wobble) * self.wobble_amp
        self.rotation += self.rot_speed
        self.pulse += self.pulse_speed
        if self.y < -80:
            self.reset()

    def draw(self, painter):
        pulse = 0.9 + 0.1 * math.sin(self.pulse)
        s = self.size * pulse

        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(math.degrees(self.rotation))

        # 外发光
        grad = QRadialGradient(0, 0, s * 1.5)
        grad.setColorAt(0, QColor(*self.color, self.alpha // 3))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawEllipse(int(-s * 1.5), int(-s * 1.5), int(s * 3), int(s * 3))

        # 爱心填充
        path = heart_path(0, 0, s)
        painter.setBrush(QColor(*self.color, self.alpha))
        painter.setPen(QPen(QColor(255, 255, 255, self.alpha // 2), 1))
        painter.drawPath(path)

        painter.restore()


class FloatingHeartsOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="FloatingHearts")
        self.hearts = [Heart(self.W, self.H) for _ in range(NUM_HEARTS)]
        self.sparkles = []

    def on_regenerate(self):
        for h in self.hearts:
            h.reset()

    def update_scene(self):
        for h in self.hearts:
            h.update()

        # 随机闪光点
        if random.random() < 0.3:
            self.sparkles.append({
                'x': random.uniform(0, self.W),
                'y': random.uniform(0, self.H),
                'life': random.uniform(15, 30),
                'max_life': 30,
                'size': random.uniform(1, 3),
            })
        for sp in self.sparkles:
            sp['life'] -= 1
        self.sparkles = [sp for sp in self.sparkles if sp['life'] > 0]

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 18))

        for h in self.hearts:
            h.draw(painter)

        # 闪光点
        for sp in self.sparkles:
            alpha = int(255 * sp['life'] / sp['max_life'])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, alpha))
            painter.drawEllipse(int(sp['x'] - sp['size']), int(sp['y'] - sp['size']),
                                int(sp['size'] * 2), int(sp['size'] * 2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FloatingHeartsOverlay()
    win.show()
    sys.exit(app.exec())
