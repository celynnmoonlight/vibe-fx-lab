"""014 爱心动画故事

阶段流程（循环播放）：
  1. 飞出来：大量小爱心从屏幕四周飞入并铺满
  2. 铺满停留：自由漂浮闪烁
  3. 汇聚：所有爱心汇聚成一个巨大的爱心
  4. 大爱心跳动：完整大爱心短暂停留
  5. 爆炸：彩色小爱心炸开，并冒出大量粉色泡泡
  6. 泡泡飘动：粉色泡泡缓慢上浮
  7. 祝福语：泡泡变成一句句爱的祝福文字
  8. 淡出并重新开始
"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QRadialGradient, QFont
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

# ---------- 调参 ----------
NUM_HEARTS    = 90      # 飞出的爱心数量
NUM_BUBBLES   = 55      # 爆炸后的泡泡数量
NUM_BLESSINGS = 26      # 祝福语数量

# 各阶段帧数（@60fps）
PHASE_FLY     = 110     # 飞入铺满 ~1.8s
PHASE_FILL    = 60      # 铺满停留 1s
PHASE_CONVERGE = 110    # 汇聚 ~1.8s
PHASE_BIG     = 50      # 大爱心跳动 ~0.8s
PHASE_EXPLODE = 35      # 爆炸 ~0.6s
PHASE_BUBBLE  = 70      # 泡泡上浮 ~1.2s
PHASE_BLESS   = 200     # 祝福语显示 ~3.3s
PHASE_FADE    = 60      # 淡出

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

BLESSINGS = [
    "我爱你", "永远在一起", "LOVE", "幸福", "心动",
    "520", "1314", "比心", "喜欢你", "守护",
    "心心相印", "白头偕老", "Forever", "Be Mine", "Sweet",
    "想你", "陪你到老", "不离不弃", "执子之手", "与子偕老",
    "XOXO", "My Love", "甜蜜", "抱抱", "亲亲", "好喜欢你",
]

# 阶段枚举
P_FLY, P_FILL, P_CONVERGE, P_BIG, P_EXPLODE, P_BUBBLE, P_BLESS, P_FADE = range(8)
PHASE_NAMES = ["飞出来", "铺满", "汇聚", "大爱心", "爆炸", "泡泡", "祝福", "淡出"]


# ---------- 工具：爱心贝塞尔路径 ----------
def heart_path(cx, cy, size, scale=1.0):
    path = QPainterPath()
    s = size * scale
    path.moveTo(cx, cy + s * 0.35)
    path.cubicTo(cx - s * 0.5, cy - s * 0.25, cx - s, cy + s * 0.15, cx, cy + s * 0.85)
    path.moveTo(cx, cy + s * 0.35)
    path.cubicTo(cx + s * 0.5, cy - s * 0.25, cx + s, cy + s * 0.15, cx, cy + s * 0.85)
    return path


def big_heart_points(n, w, h):
    """大爱心参数曲线上的 n 个采样点（归一化后居中）"""
    cx, cy = w / 2, h / 2
    size = min(w, h) * 0.30
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * size / 16, cy + y * size / 16))
    return pts


# ---------- 小爱心 ----------
class Heart:
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.size = random.uniform(28, 70)
        self.color = random.choice(HEART_COLORS)
        self.alpha = 0
        self.rot = random.uniform(-25, 25)
        self.rot_speed = random.uniform(-0.4, 0.4)
        self.pulse = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.05, 0.10)
        self.visible = False
        self.gathered = False
        self._init_fly()

    def _init_fly(self):
        """从屏幕外某一边飞入"""
        edge = random.choice([0, 1, 2, 3])  # 上右下左
        if edge == 0:
            self.x = random.uniform(0, self.W)
            self.y = -self.size - random.uniform(0, 200)
        elif edge == 1:
            self.x = self.W + self.size + random.uniform(0, 200)
            self.y = random.uniform(0, self.H)
        elif edge == 2:
            self.x = random.uniform(0, self.W)
            self.y = self.H + self.size + random.uniform(0, 200)
        else:
            self.x = -self.size - random.uniform(0, 200)
            self.y = random.uniform(0, self.H)
        self.tx = random.uniform(self.size, self.W - self.size)
        self.ty = random.uniform(self.size, self.H - self.size)
        self.fly_delay = random.randint(0, 25)  # 错峰飞入

    def start_gather(self, tx, ty):
        self.tx, self.ty = tx, ty
        self.gathered = True

    def fade_out(self):
        self.fading = True

    def set_invisible(self):
        self.visible = False

    def update_fly(self, t, dur):
        """t 0..dur 缓动到 (tx, ty)"""
        if self.fly_delay > 0:
            self.fly_delay -= 1
            return
        self.visible = True
        k = min(1.0, t / max(1, dur - self.fly_delay))
        k = 1 - (1 - k) ** 3  # easeOutCubic
        self.x = self.x + (self.tx - self.x) * (0.08 + 0.12 * k)
        self.y = self.y + (self.ty - self.y) * (0.08 + 0.12 * k)
        self.alpha = int(180 + 60 * k)
        if k > 0.4:
            self.tx += random.uniform(-0.4, 0.4)
            self.ty += random.uniform(-0.4, 0.4)
        self.rot += self.rot_speed

    def update_drift(self):
        """铺满阶段自由漂浮"""
        self.tx += random.uniform(-0.5, 0.5)
        self.ty += random.uniform(-0.5, 0.5)
        self.tx = max(self.size, min(self.W - self.size, self.tx))
        self.ty = max(self.size, min(self.H - self.size, self.ty))
        self.x += (self.tx - self.x) * 0.05
        self.y += (self.ty - self.y) * 0.05
        self.alpha = int(180 + 40 * math.sin(self.pulse))
        self.pulse += self.pulse_speed
        self.rot += self.rot_speed

    def update_gather(self, t, dur):
        k = min(1.0, t / dur)
        k = 1 - (1 - k) ** 2  # easeOutQuad
        # 保留起点：当前 (x, y) → (tx, ty)
        if not hasattr(self, "_gx"):
            self._gx, self._gy = self.x, self.y
        self.x = self._gx + (self.tx - self._gx) * k
        self.y = self._gy + (self.ty - self._gy) * k
        self.alpha = int(255 * (0.6 + 0.4 * k))
        self.rot += self.rot_speed * 0.5

    def update_big(self, t, dur):
        """聚成大爱心后整体脉动"""
        k = t / dur
        self.pulse += self.pulse_speed
        s = 1.0 + 0.05 * math.sin(self.pulse * 1.5)
        # 让采样点本身随整体脉动外扩
        cx, cy = self.W / 2, self.H / 2
        dx, dy = self.tx - cx, self.ty - cy
        self.x = cx + dx * s
        self.y = cy + dy * s
        self.alpha = 255

    def update_explode(self, t, dur):
        k = min(1.0, t / dur)
        # 向外炸开
        cx, cy = self.W / 2, self.H / 2
        dx = self.tx - cx
        dy = self.ty - cy
        d = math.hypot(dx, dy) or 1
        ux, uy = dx / d, dy / d
        # 各自的速度方向（带一点随机）
        if not hasattr(self, "_ex_v"):
            a = math.atan2(dy, dx) + random.uniform(-0.4, 0.4)
            sp = random.uniform(6, 14)
            self._ex_v = (math.cos(a) * sp, math.sin(a) * sp)
        vx, vy = self._ex_v
        self.x += vx
        self.y += vy
        self.rot += self.rot_speed * 2
        self.alpha = int(255 * (1 - k * 0.7))
        self.size *= 0.985  # 越飞越小

    def draw(self, painter):
        if not self.visible or self.alpha <= 0:
            return
        s = self.size
        a = max(0, min(255, self.alpha))
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rot)

        glow = QRadialGradient(0, 0, s * 2.0)
        glow.setColorAt(0, QColor(*self.color, min(a // 2, 110)))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(int(-s * 2), int(-s * 2), int(s * 4), int(s * 4))

        path = heart_path(0, 0, s)
        painter.setBrush(QColor(*self.color, a))
        painter.setPen(QPen(QColor(255, 255, 255, min(a // 2, 130)), 1.5))
        painter.drawPath(path)
        painter.restore()


# ---------- 粉色泡泡 ----------
class Bubble:
    def __init__(self, w, h, x, y):
        self.W, self.H = w, h
        self.x, self.y = x, y
        self.r = random.uniform(18, 38)
        self.vx = random.uniform(-0.6, 0.6)
        self.vy = random.uniform(-1.6, -0.6)
        self.alpha = 0
        self.alive = True
        self.wobble = random.uniform(0, math.pi * 2)
        self.color = random.choice([
            (255, 200, 220), (255, 180, 210), (255, 220, 235),
            (255, 160, 200), (255, 240, 245), (255, 195, 225),
        ])
        self.grow = random.uniform(0.3, 0.6)

    def update(self, t, dur):
        k = min(1.0, t / dur)
        # 出生放大
        if t < 20:
            self.alpha = int(255 * (t / 20))
        else:
            self.alpha = 240
        self.wobble += 0.05
        self.x += self.vx + math.sin(self.wobble) * 0.4
        self.y += self.vy
        self.r += self.grow * 0.05
        if self.y < -self.r:
            self.alive = False

    def draw(self, painter):
        if not self.alive:
            return
        grad = QRadialGradient(self.x - self.r * 0.3, self.y - self.r * 0.3, self.r * 1.2)
        c = QColor(*self.color, self.alpha)
        grad.setColorAt(0, QColor(255, 255, 255, min(255, self.alpha)))
        grad.setColorAt(0.35, c)
        grad.setColorAt(1, QColor(*self.color, max(0, self.alpha - 80)))
        painter.setPen(QPen(QColor(255, 255, 255, min(180, self.alpha)), 1))
        painter.setBrush(grad)
        painter.drawEllipse(int(self.x - self.r), int(self.y - self.r), int(self.r * 2), int(self.r * 2))
        # 高光
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, min(220, self.alpha)))
        painter.drawEllipse(int(self.x - self.r * 0.5), int(self.y - self.r * 0.55),
                            int(self.r * 0.35), int(self.r * 0.25))


# ---------- 祝福语 ----------
class Blessing:
    def __init__(self, w, h, x, y, text):
        self.W, self.H = w, h
        self.x, self.y = x, y
        self.tx = random.uniform(w * 0.10, w * 0.90)
        self.ty = random.uniform(h * 0.18, h * 0.82)
        self.text = text
        self.alpha = 0
        self.scale = 0.3
        self.alive = True
        self.color = random.choice(HEART_COLORS + [(255, 100, 150)])
        self.wobble = random.uniform(0, math.pi * 2)

    def update(self, t, dur):
        k = min(1.0, t / dur)
        if t < 25:
            self.alpha = int(255 * (t / 25))
            self.scale = 0.3 + 0.7 * (t / 25)
        elif t < dur - 60:
            self.alpha = 255
            self.scale = 1.0
        else:
            fade = max(0, (dur - t) / 60)
            self.alpha = int(255 * fade)
            self.scale = 1.0 + (1 - fade) * 0.3
        # 飘向目标位置
        self.x += (self.tx - self.x) * 0.04
        self.y += (self.ty - self.y) * 0.04
        self.wobble += 0.04
        if t > dur - 60 and self.alpha <= 0:
            self.alive = False

    def draw(self, painter):
        if not self.alive or self.alpha <= 0:
            return
        size = max(12, int(48 * self.scale))
        font = QFont("Microsoft YaHei", size, QFont.Weight.Bold)
        painter.setFont(font)
        # 阴影
        painter.setPen(QColor(120, 30, 60, self.alpha // 2))
        painter.drawText(int(self.x + 3 + math.sin(self.wobble) * 2),
                         int(self.y + 3), self.text)
        # 主文字
        painter.setPen(QColor(*self.color, self.alpha))
        painter.drawText(int(self.x + math.sin(self.wobble) * 2),
                         int(self.y), self.text)


# ---------- 主场景 ----------
class HeartsStoryOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="HeartsStory")
        self.hearts = [Heart(self.W, self.H) for _ in range(NUM_HEARTS)]
        self.bubbles = []
        self.blessings = []
        self.phase = P_FLY
        self.phase_t = 0
        self.big_pulse = 0
        self.explode_flash = 0
        self._setup_gather_targets()
        # 初始隐藏
        for h in self.hearts:
            h.alpha = 0
            h.visible = False

    def _setup_gather_targets(self):
        pts = big_heart_points(len(self.hearts), self.W, self.H)
        random.shuffle(pts)
        for h, (tx, ty) in zip(self.hearts, pts):
            h.tx, h.ty = tx, ty

    def on_regenerate(self):
        """Space 重新开始整个故事"""
        self.phase = P_FLY
        self.phase_t = 0
        self.bubbles.clear()
        self.blessings.clear()
        self._setup_gather_targets()
        for h in self.hearts:
            h._init_fly()
            h.alpha = 0
            h.visible = False
            h.fading = False
            h.gathered = False
            h._gx = h._gy = None
            h._ex_v = None

    def update_scene(self):
        self.phase_t += 1
        if self.phase == P_FLY:
            for h in self.hearts:
                h.update_fly(self.phase_t, PHASE_FLY)
            if self.phase_t >= PHASE_FLY:
                self.phase = P_FILL
                self.phase_t = 0
        elif self.phase == P_FILL:
            for h in self.hearts:
                h.update_drift()
            if self.phase_t >= PHASE_FILL:
                # 给每颗心一个目标（爱心曲线上对应位置）
                pts = big_heart_points(len(self.hearts), self.W, self.H)
                random.shuffle(pts)
                for h, (tx, ty) in zip(self.hearts, pts):
                    h.start_gather(tx, ty)
                self.phase = P_CONVERGE
                self.phase_t = 0
        elif self.phase == P_CONVERGE:
            for h in self.hearts:
                h.update_gather(self.phase_t, PHASE_CONVERGE)
            if self.phase_t >= PHASE_CONVERGE:
                self.phase = P_BIG
                self.phase_t = 0
        elif self.phase == P_BIG:
            self.big_pulse += 1
            for h in self.hearts:
                h.update_big(self.phase_t, PHASE_BIG)
            if self.phase_t >= PHASE_BIG:
                self.phase = P_EXPLODE
                self.phase_t = 0
                self.explode_flash = 18
                # 在中心生成泡泡
                cx, cy = self.W / 2, self.H / 2
                for _ in range(NUM_BUBBLES):
                    a = random.uniform(0, math.pi * 2)
                    r = random.uniform(0, 40)
                    self.bubbles.append(Bubble(self.W, self.H,
                                               cx + math.cos(a) * r,
                                               cy + math.sin(a) * r))
        elif self.phase == P_EXPLODE:
            for h in self.hearts:
                h.update_explode(self.phase_t, PHASE_EXPLODE)
            if self.explode_flash > 0:
                self.explode_flash -= 1
            if self.phase_t >= PHASE_EXPLODE:
                self.phase = P_BUBBLE
                self.phase_t = 0
        elif self.phase == P_BUBBLE:
            for b in self.bubbles:
                b.update(self.phase_t, PHASE_BUBBLE)
            self.bubbles = [b for b in self.bubbles if b.alive]
            if self.phase_t >= PHASE_BUBBLE:
                # 泡泡变成祝福语
                self.blessings.clear()
                random.shuffle(BLESSINGS)
                for i, b in enumerate(self.bubbles[:NUM_BLESSINGS]):
                    self.blessings.append(Blessing(self.W, self.H, b.x, b.y,
                                                  BLESSINGS[i % len(BLESSINGS)]))
                self.bubbles.clear()
                self.phase = P_BLESS
                self.phase_t = 0
        elif self.phase == P_BLESS:
            for bl in self.blessings:
                bl.update(self.phase_t, PHASE_BLESS)
            self.blessings = [b for b in self.blessings if b.alive]
            if self.phase_t >= PHASE_BLESS:
                self.phase = P_FADE
                self.phase_t = 0
        elif self.phase == P_FADE:
            for bl in self.blessings:
                bl.update(self.phase_t + PHASE_BLESS, PHASE_BLESS)
            self.blessings = [b for b in self.blessings if b.alive]
            if self.phase_t >= PHASE_FADE:
                # 重新开始整段故事
                self.on_regenerate()

    def draw_scene(self, painter: QPainter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 极淡粉雾底
        painter.fillRect(0, 0, self.W, self.H, QColor(255, 220, 230, 8))

        # 爆炸瞬间全屏闪光
        if self.explode_flash > 0:
            a = int(120 * self.explode_flash / 18)
            painter.fillRect(0, 0, self.W, self.H, QColor(255, 240, 245, a))

        # 爱心
        for h in sorted(self.hearts, key=lambda x: -x.size):
            h.draw(painter)

        # 泡泡
        for b in self.bubbles:
            b.draw(painter)

        # 祝福语
        for bl in self.blessings:
            bl.draw(painter)

        # 左上角阶段提示
        font = QFont("Microsoft YaHei", 22, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 180))
        painter.drawText(20, 50, f"阶段: {PHASE_NAMES[self.phase]}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HeartsStoryOverlay()
    win.show()
    sys.exit(app.exec())
