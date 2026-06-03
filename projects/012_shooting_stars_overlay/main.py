"""012 流星许愿悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

NUM_BG_STARS = 150
STAR_COLORS = [
    (255, 255, 255),
    (200, 220, 255),
    (255, 220, 255),
    (220, 255, 255),
    (255, 255, 220),
]


class BgStar:
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h * 0.7)
        self.size = random.uniform(0.5, 2.5)
        self.color = random.choice(STAR_COLORS)
        self.twinkle = random.uniform(0, math.pi * 2)
        self.twinkle_speed = random.uniform(0.03, 0.12)

    def update(self):
        self.twinkle += self.twinkle_speed

    def draw(self, painter):
        alpha = int(100 + 155 * math.sin(self.twinkle))
        s = self.size * (0.6 + 0.4 * math.sin(self.twinkle))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*self.color, alpha))
        painter.drawEllipse(int(self.x - s), int(self.y - s), int(s * 2), int(s * 2))


class ShootingStar:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.active = False
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.trail = []
        self.life = 0
        self.max_life = 0
        self.tail_len = 0
        self.color = (255, 255, 255)
        self.size = 0

    def launch(self):
        self.active = True
        # 从左上或右上区域出发
        side = random.choice(['left', 'right'])
        if side == 'left':
            self.x = random.uniform(0, self.w * 0.3)
            self.y = random.uniform(0, self.h * 0.2)
            angle = random.uniform(0.3, 0.8)  # 右下
        else:
            self.x = random.uniform(self.w * 0.7, self.w)
            self.y = random.uniform(0, self.h * 0.2)
            angle = random.uniform(2.3, 2.8)  # 左下

        speed = random.uniform(8, 15)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.uniform(2, 4)
        self.tail_len = random.randint(25, 50)
        self.max_life = random.randint(40, 70)
        self.life = self.max_life
        self.trail.clear()

        # 颜色：白、淡蓝、淡紫、淡金
        self.color = random.choice([
            (255, 255, 255),
            (200, 220, 255),
            (220, 200, 255),
            (255, 240, 200),
            (255, 220, 240),
        ])

    def update(self):
        if not self.active:
            return

        self.trail.append((self.x, self.y))
        if len(self.trail) > self.tail_len:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # 轻微重力
        self.life -= 1

        if self.life <= 0 or self.x > self.w + 100 or self.y > self.h + 100:
            self.active = False

    def draw(self, painter):
        if not self.active:
            return

        ratio = self.life / self.max_life

        # 尾迹
        for i, (tx, ty) in enumerate(self.trail):
            t = i / len(self.trail) if self.trail else 0
            alpha = int(255 * t * ratio)
            s = self.size * t * 0.8
            # 发光
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(*self.color, alpha // 3))
            painter.drawEllipse(int(tx - s * 3), int(ty - s * 3), int(s * 6), int(s * 6))
            # 核心
            painter.setBrush(QColor(*self.color, alpha))
            painter.drawEllipse(int(tx - s), int(ty - s), int(s * 2), int(s * 2))

        # 流星头部（大光晕）
        s = self.size
        grad = QRadialGradient(self.x, self.y, s * 5)
        grad.setColorAt(0, QColor(*self.color, int(200 * ratio)))
        grad.setColorAt(0.3, QColor(*self.color, int(80 * ratio)))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawEllipse(int(self.x - s * 5), int(self.y - s * 5), int(s * 10), int(s * 10))

        # 流星核心
        painter.setBrush(QColor(255, 255, 255, int(255 * ratio)))
        painter.drawEllipse(int(self.x - s), int(self.y - s), int(s * 2), int(s * 2))


class WishOnStarOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="ShootingStars")
        self.stars = [BgStar(self.W, self.H) for _ in range(NUM_BG_STARS)]
        self.shooters = [ShootingStar(self.W, self.H) for _ in range(3)]
        self.timer_count = 0

    def on_regenerate(self):
        self.stars = [BgStar(self.W, self.H) for _ in range(NUM_BG_STARS)]

    def update_scene(self):
        self.timer_count += 1
        for s in self.stars:
            s.update()

        # 随机发射流星
        if self.timer_count % random.randint(30, 80) == 0:
            for shooter in self.shooters:
                if not shooter.active:
                    shooter.launch()
                    break

        for shooter in self.shooters:
            shooter.update()

    def draw_scene(self, painter: QPainter):
        # 深蓝夜空背景（半透明叠加形成拖尾）
        painter.fillRect(0, 0, self.W, self.H, QColor(5, 5, 20, 30))

        for s in self.stars:
            s.draw(painter)

        for shooter in self.shooters:
            shooter.draw(painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WishOnStarOverlay()
    win.show()
    sys.exit(app.exec())
