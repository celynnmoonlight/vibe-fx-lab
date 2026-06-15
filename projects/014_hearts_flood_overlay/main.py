"""014 爱心铺满屏幕悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QRadialGradient
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_HEARTS = 110          # 大量爱心
NUM_SPARKLES = 80         # 伴随闪光

HEART_COLORS = [
    (255, 60, 120),    # 桃红
    (255, 90, 150),    # 粉红
    (255, 120, 180),   # 樱花粉
    (255, 30, 90),     # 玫红
    (255, 150, 200),   # 浅粉
    (255, 180, 220),   # 蜜桃粉
    (235, 90, 180),    # 紫红
    (255, 200, 230),   # 嫩粉
    (220, 80, 150),    # 紫粉
    (255, 100, 130),   # 西瓜红
]


def heart_path(cx, cy, size):
    """标准心形贝塞尔路径"""
    path = QPainterPath()
    s = size
    path.moveTo(cx, cy + s * 0.35)
    path.cubicTo(cx - s * 0.5, cy - s * 0.25, cx - s, cy + s * 0.15, cx, cy + s * 0.85)
    path.moveTo(cx, cy + s * 0.35)
    path.cubicTo(cx + s * 0.5, cy - s * 0.25, cx + s, cy + s * 0.15, cx, cy + s * 0.85)
    return path


class BigHeart:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        # 大尺寸：60 ~ 180
        self.size = random.uniform(60, 180)
        # 任意位置
        self.x = random.uniform(self.size, self.w - self.size)
        self.y = random.uniform(self.size, self.h - self.size)
        # 缓慢漂浮速度
        self.vx = random.uniform(-0.6, 0.6)
        self.vy = random.uniform(-0.6, 0.6)
        # 摆动
        self.wobble = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.01, 0.04)
        self.wobble_amp = random.uniform(0.4, 1.6)
        # 旋转
        self.rotation = random.uniform(-30, 30)
        self.rot_speed = random.uniform(-0.4, 0.4)
        # 颜色与透明度
        self.color = random.choice(HEART_COLORS)
        self.alpha = random.randint(160, 235)
        # 心跳脉动
        self.pulse = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.04, 0.10)
        # 整体缓慢呼吸的透明度
        self.fade_phase = random.uniform(0, math.pi * 2)
        self.fade_speed = random.uniform(0.005, 0.02)
        self.alpha_min = random.randint(110, 160)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * self.wobble_amp
        self.y += math.cos(self.wobble * 0.7) * self.wobble_amp
        self.rotation += self.rot_speed
        self.pulse += self.pulse_speed
        self.fade_phase += self.fade_speed

        # 边界软回弹
        m = self.size * 0.6
        if self.x < m:
            self.vx += 0.05
        elif self.x > self.w - m:
            self.vx -= 0.05
        if self.y < m:
            self.vy += 0.05
        elif self.y > self.h - m:
            self.vy -= 0.05

        # 速度阻尼
        self.vx = max(-1.2, min(1.2, self.vx * 0.99))
        self.vy = max(-1.2, min(1.2, self.vy * 0.99))

    def current_alpha(self):
        breath = 0.5 + 0.5 * math.sin(self.fade_phase)
        return int(self.alpha_min + (self.alpha - self.alpha_min) * breath)

    def draw(self, painter):
        pulse = 0.88 + 0.12 * math.sin(self.pulse)
        s = self.size * pulse
        a = self.current_alpha()

        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rotation)

        # 外发光
        glow = QRadialGradient(0, 0, s * 2.2)
        glow.setColorAt(0, QColor(*self.color, min(a // 2, 110)))
        glow.setColorAt(0.5, QColor(*self.color, min(a // 4, 60)))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(int(-s * 2.2), int(-s * 2.2), int(s * 4.4), int(s * 4.4))

        # 主体爱心
        path = heart_path(0, 0, s)
        painter.setBrush(QColor(*self.color, a))
        painter.setPen(QPen(QColor(255, 255, 255, min(a // 2, 130)), 2))
        painter.drawPath(path)

        # 高光
        hl = QRadialGradient(-s * 0.3, -s * 0.35, s * 0.45)
        hl.setColorAt(0, QColor(255, 255, 255, min(a, 180)))
        hl.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(hl)
        painter.drawEllipse(int(-s * 0.7), int(-s * 0.7), int(s * 1.0), int(s * 0.8))

        painter.restore()


class Sparkle:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.active = False

    def emit(self):
        self.active = True
        self.x = random.uniform(0, self.w)
        self.y = random.uniform(0, self.h)
        self.life = random.uniform(20, 50)
        self.max_life = self.life
        self.size = random.uniform(2, 5)
        self.color = random.choice(HEART_COLORS + [(255, 255, 255)])

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
        s = self.size * (0.6 + 0.4 * math.sin(self.life * 0.4))

        painter.setPen(QPen(QColor(*self.color, alpha), 1))
        painter.drawLine(int(self.x - s * 3), int(self.y), int(self.x + s * 3), int(self.y))
        painter.drawLine(int(self.x), int(self.y - s * 3), int(self.x), int(self.y + s * 3))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, alpha))
        painter.drawEllipse(int(self.x - s), int(self.y - s), int(s * 2), int(s * 2))


class HeartsFloodOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="HeartsFlood")
        self.hearts = [BigHeart(self.W, self.H) for _ in range(NUM_HEARTS)]
        self.sparkles = [Sparkle(self.W, self.H) for _ in range(NUM_SPARKLES)]
        self.spawn_timer = 0

    def on_regenerate(self):
        for h in self.hearts:
            h.reset()

    def update_scene(self):
        self.spawn_timer += 1
        for h in self.hearts:
            h.update()

        if self.spawn_timer % 4 == 0:
            for sp in self.sparkles:
                if not sp.active:
                    sp.emit()
                    break
        # 偶发额外闪光
        if random.random() < 0.25:
            for sp in self.sparkles:
                if not sp.active:
                    sp.emit()
                    break

        for sp in self.sparkles:
            sp.update()

    def draw_scene(self, painter: QPainter):
        # 极淡的粉色雾底，让背景有一点点温度
        painter.fillRect(0, 0, self.W, self.H, QColor(255, 200, 220, 6))

        for sp in self.sparkles:
            sp.draw(painter)

        # 按 size 从大到小画，营造层次
        for h in sorted(self.hearts, key=lambda x: -x.size):
            h.draw(painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HeartsFloodOverlay()
    win.show()
    sys.exit(app.exec())
