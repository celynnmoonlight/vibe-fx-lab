"""003 液化霓虹文字悬浮层"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QFont, QFontMetricsF,
    QPainterPath, QLinearGradient
)
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow
from shared.colors import random_neon, lerp_color

TEXT = "VIBE FX"
FONT_SIZE = 280
NUM_TRAILS = 8
WAVE_SPEED = 0.03
DRIP_CHANCE = 0.02


class Drip:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vy = random.uniform(1, 4)
        self.life = random.uniform(40, 80)
        self.max_life = self.life
        self.color = color
        self.size = random.uniform(2, 5)

    def update(self):
        self.y += self.vy
        self.vy += 0.08
        self.life -= 1

    @property
    def alive(self):
        return self.life > 0


class LiquidTextOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="LiquidNeonText")
        self.text = TEXT
        self.time = 0
        self.colors = [random_neon() for _ in range(NUM_TRAILS)]
        self.drips: list[Drip] = []
        self.cx, self.cy = self.W // 2, self.H // 2

    def on_regenerate(self):
        self.colors = [random_neon() for _ in range(NUM_TRAILS)]
        self.drips.clear()

    def update_scene(self):
        self.time += WAVE_SPEED

        # 产生滴落
        if random.random() < DRIP_CHANCE:
            font = QFont("Arial", FONT_SIZE, QFont.Weight.Bold)
            fm = QFontMetricsF(font)
            tw = fm.horizontalAdvance(self.text)
            x = self.cx - tw / 2 + random.uniform(0, tw)
            y = self.cy + fm.descent() + 10
            self.drips.append(Drip(x, y, random.choice(self.colors)))

        for d in self.drips:
            d.update()
        self.drips = [d for d in self.drips if d.alive]

    def _make_path(self, text, font, offset_x=0, offset_y=0):
        path = QPainterPath()
        path.addText(QPointF(offset_x, offset_y), font, text)
        return path

    def draw_scene(self, painter: QPainter):
        painter.fillRect(0, 0, self.W, self.H, QColor(0, 0, 0, 25))

        font = QFont("Arial", FONT_SIZE, QFont.Weight.Bold)
        fm = QFontMetricsF(font)
        tw = fm.horizontalAdvance(self.text)
        tx = self.cx - tw / 2
        ty = self.cy + fm.ascent() * 0.35

        # 液化拖尾层
        for i in range(NUM_TRAILS):
            offset = math.sin(self.time + i * 0.6) * (8 + i * 3)
            y_off = math.cos(self.time * 0.7 + i * 0.5) * (5 + i * 2)
            alpha = int(120 * (1 - i / NUM_TRAILS))
            color = self.colors[i]

            path = self._make_path(self.text, font, tx + offset, ty + y_off + i * 6)
            pen = QPen(QColor(*color, alpha), 2)
            painter.setPen(pen)
            painter.setBrush(QColor(*color, alpha // 3))
            painter.drawPath(path)

        # 主文字
        main_path = self._make_path(self.text, font, tx, ty)
        grad = QLinearGradient(tx, ty - FONT_SIZE, tx + tw, ty + 30)
        for i, c in enumerate(self.colors[:4]):
            grad.setColorAt(i / 3, QColor(*c, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawPath(main_path)

        # 外发光
        glow_path = self._make_path(self.text, font, tx, ty)
        painter.setPen(QPen(QColor(*self.colors[0], 60), 8))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(glow_path)

        # 滴落粒子
        for d in self.drips:
            alpha = int(255 * d.life / d.max_life)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(*d.color, alpha))
            painter.drawEllipse(int(d.x - d.size), int(d.y - d.size),
                                int(d.size * 2), int(d.size * 2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LiquidTextOverlay()
    win.show()
    sys.exit(app.exec())
