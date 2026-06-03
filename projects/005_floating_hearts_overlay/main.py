"""005 飘浮爱心悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QRadialGradient
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_HEARTS = 80
NUM_MINI_HEARTS = 60
NUM_SPARKLES = 100
PINK_COLORS = [
    (255, 105, 180),
    (255, 182, 193),
    (255, 20, 147),
    (255, 160, 200),
    (255, 192, 203),
    (255, 140, 180),
    (238, 130, 238),
    (255, 100, 150),
    (255, 255, 200),  # 暖白
    (200, 220, 255),  # 淡蓝
]


def heart_path(cx, cy, size):
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
        self.x = random.uniform(30, self.w - 30)
        self.y = self.h + random.uniform(0, 300)
        self.size = random.uniform(8, 50)
        self.vy = random.uniform(-2.0, -0.3)
        self.vx = random.uniform(-0.8, 0.8)
        self.wobble = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.02, 0.06)
        self.wobble_amp = random.uniform(0.5, 3.0)
        self.rotation = random.uniform(-0.5, 0.5)
        self.rot_speed = random.uniform(-0.01, 0.01)
        self.color = random.choice(PINK_COLORS)
        self.alpha = random.randint(120, 255)
        self.pulse = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.03, 0.08)

    def update(self):
        self.y += self.vy
        self.wobble += self.wobble_speed
        self.x += self.vx + math.sin(self.wobble) * self.wobble_amp
        self.rotation += self.rot_speed
        self.pulse += self.pulse_speed
        if self.y < -80:
            self.reset()

    def draw(self, painter):
        pulse = 0.85 + 0.15 * math.sin(self.pulse)
        s = self.size * pulse

        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(math.degrees(self.rotation))

        # 外发光
        grad = QRadialGradient(0, 0, s * 2)
        grad.setColorAt(0, QColor(*self.color, self.alpha // 2))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawEllipse(int(-s * 2), int(-s * 2), int(s * 4), int(s * 4))

        # 爱心填充
        path = heart_path(0, 0, s)
        painter.setBrush(QColor(*self.color, self.alpha))
        painter.setPen(QPen(QColor(255, 255, 255, self.alpha // 3), 1))
        painter.drawPath(path)

        painter.restore()


class MiniHeartParticle:
    """小爱心粒子，从大爱心身上飘出"""
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.active = False

    def emit(self, x, y, color):
        self.active = True
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.3, 2.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 0.5
        self.size = random.uniform(3, 10)
        self.color = color
        self.life = random.uniform(30, 80)
        self.max_life = self.life
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-3, 3)

    def update(self):
        if not self.active:
            return
        self.x += self.vx
        self.y += self.vy
        self.vy -= 0.01
        self.rotation += self.rot_speed
        self.life -= 1
        if self.life <= 0:
            self.active = False

    def draw(self, painter):
        if not self.active:
            return
        ratio = self.life / self.max_life
        alpha = int(255 * ratio)
        s = self.size * ratio

        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rotation)
        path = heart_path(0, 0, s)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*self.color, alpha))
        painter.drawPath(path)
        painter.restore()


class Sparkle:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.active = False

    def emit(self):
        self.active = True
        self.x = random.uniform(0, self.w)
        self.y = random.uniform(0, self.h)
        self.life = random.uniform(10, 40)
        self.max_life = self.life
        self.size = random.uniform(1, 4)
        self.color = random.choice(PINK_COLORS + [(255, 255, 255), (255, 255, 200)])

    def update(self):
        if not self.active:
            return
        self.life -= 1
        if self.life <= 0:
            self.active = False

    def draw(self, painter):
        if not self.active:
            return
        ratio = self.life / self.max_life
        alpha = int(255 * ratio)
        s = self.size * (0.5 + 0.5 * math.sin(self.life * 0.3))

        # 十字闪光
        painter.setPen(QPen(QColor(*self.color, alpha), 1))
        painter.drawLine(int(self.x - s * 3), int(self.y), int(self.x + s * 3), int(self.y))
        painter.drawLine(int(self.x), int(self.y - s * 3), int(self.x), int(self.y + s * 3))
        # 中心点
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, alpha))
        painter.drawEllipse(int(self.x - s), int(self.y - s), int(s * 2), int(s * 2))


class FloatingHeartsOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="FloatingHearts")
        self.hearts = [Heart(self.W, self.H) for _ in range(NUM_HEARTS)]
        self.mini_hearts = [MiniHeartParticle(self.W, self.H) for _ in range(NUM_MINI_HEARTS)]
        self.sparkles = [Sparkle(self.W, self.H) for _ in range(NUM_SPARKLES)]
        self.emit_timer = 0

    def on_regenerate(self):
        for h in self.hearts:
            h.reset()

    def update_scene(self):
        self.emit_timer += 1

        for h in self.hearts:
            h.update()

        # 从大爱心上持续喷出小爱心
        if self.emit_timer % 3 == 0:
            for mh in self.mini_hearts:
                if not mh.active:
                    src = random.choice(self.hearts)
                    mh.emit(src.x, src.y, src.color)
                    break

        for mh in self.mini_hearts:
            mh.update()

        # 持续产生闪光
        if random.random() < 0.4:
            for sp in self.sparkles:
                if not sp.active:
                    sp.emit()
                    break

        for sp in self.sparkles:
            sp.update()

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 18))

        for sp in self.sparkles:
            sp.draw(painter)

        for mh in self.mini_hearts:
            mh.draw(painter)

        for h in self.hearts:
            h.draw(painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FloatingHeartsOverlay()
    win.show()
    sys.exit(app.exec())
