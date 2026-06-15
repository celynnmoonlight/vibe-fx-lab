"""015 爱心故事 终章（Hearts Story Finale）

完整 5 阶段故事：
  1. 双爱心嵌套飞出    —— 两个大爱心带光晕沿曲线优雅飞出，形成嵌套
  2. 心形流星雨         —— 母爱心从顶部飘落，沿途洒出大量小爱心
  3. 爱心铺满屏幕       —— 无数小爱心从各方向飞出铺满整个屏幕
  4. 汇聚成大爱心       —— 沿心形曲线汇聚、叠加、融合成璀璨大爱心
  5. 爆炸 + 泡泡 + 祝福 —— 大爱心华丽炸成粉色泡泡，浮现爱的祝福语
"""

import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QPainterPath,
                         QRadialGradient, QLinearGradient, QFont, QPolygonF)
from PyQt6.QtWidgets import QApplication
from shared.overlay import OverlayWindow

# ============================================================
# 调参
# ============================================================
NUM_FILL_HEARTS = 110   # 阶段三铺满用的小爱心
NUM_MOTHERS     = 7     # 阶段二的母爱心数量
NUM_BUBBLES     = 60    # 爆炸后的泡泡数量
NUM_BLESSINGS   = 18    # 祝福语种类

# 各阶段帧数（@60fps）
PHASE_PAIR_FLY     = 130   # 阶段一：双爱心飞出 ~2.2s
PHASE_PAIR_HOLD    = 40    # 阶段一：嵌套停留 ~0.7s
PHASE_RAIN         = 160   # 阶段二：流星雨 ~2.7s
PHASE_FILL_FLY     = 110   # 阶段三：爱心铺满 ~1.8s
PHASE_FILL_HOLD    = 60    # 阶段三：铺满停留 ~1.0s
PHASE_CONVERGE     = 120   # 阶段四：汇聚 ~2.0s
PHASE_BIG_HOLD     = 50    # 阶段四：大爱心停留 ~0.8s
PHASE_EXPLODE      = 30    # 阶段五：爆炸 ~0.5s
PHASE_BUBBLE       = 70    # 阶段五：泡泡上浮 ~1.2s
PHASE_BLESS        = 220   # 阶段五：祝福语 ~3.7s
PHASE_FADE         = 60    # 阶段五：淡出

# 阶段枚举
(P_PAIR, P_RAIN, P_FILL, P_FILL_HOLD, P_CONVERGE,
 P_BIG, P_EXPLODE, P_BUBBLE, P_BLESS, P_FADE) = range(10)
PHASE_NAMES = ["双爱心飞出", "心形流星雨", "爱心铺满", "铺满停留",
               "汇聚大爱心", "大爱心停留", "爱心爆炸", "泡泡上浮",
               "爱的祝福", "淡出"]

# 颜色
HEART_COLORS = [
    (255, 60, 120),   (255, 90, 150),   (255, 120, 180),
    (255, 30, 90),    (255, 150, 200),  (255, 180, 220),
    (235, 90, 180),   (255, 200, 230),  (220, 80, 150),
    (255, 100, 130),  (255, 200, 100),  (255, 220, 150),
    (200, 130, 255),  (255, 160, 180),  (255, 80, 100),
]
GOLD = (255, 215, 110)
ROSE = (255, 130, 170)
WHITE = (255, 245, 250)
BUBBLE_COLORS = [
    (255, 200, 220), (255, 180, 210), (255, 220, 235),
    (255, 160, 200), (255, 240, 245), (255, 195, 225),
    (255, 175, 215), (255, 210, 230),
]

BLESSINGS = [
    "我爱你", "Forever", "甜蜜", "心动", "幸福",
    "永远在一起", "你是唯一", "天长地久", "比心", "陪伴",
    "心心相印", "白头偕老", "Be Mine", "Sweet", "想你",
    "执子之手", "与子偕老", "My Love", "XOXO", "520",
    "1314", "守护", "喜欢你", "Love U", "亲亲",
]

# ============================================================
# 工具：爱心贝塞尔路径 & 曲线采样
# ============================================================
def heart_path(cx, cy, size):
    """用贝塞尔曲线绘制一个以 (cx,cy) 为中心、size 为尺寸的爱心"""
    path = QPainterPath()
    s = size
    # 起笔点
    path.moveTo(cx, cy + s * 0.35)
    # 左侧
    path.cubicTo(cx - s * 0.5,  cy - s * 0.25,
                 cx - s * 1.0,  cy + s * 0.15,
                 cx,            cy + s * 0.85)
    # 回到起笔
    path.moveTo(cx, cy + s * 0.35)
    # 右侧
    path.cubicTo(cx + s * 0.5,  cy - s * 0.25,
                 cx + s * 1.0,  cy + s * 0.15,
                 cx,            cy + s * 0.85)
    return path


def big_heart_points(n, w, h, scale=0.30):
    """心形参数曲线上 n 个采样点（归一化，居中）"""
    cx, cy = w / 2, h / 2
    size = min(w, h) * scale
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t)
              - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * size / 16, cy + y * size / 16))
    return pts


def bezier_point(p0, p1, p2, p3, t):
    """三次贝塞尔曲线在 t 处的点"""
    u = 1 - t
    x = u**3*p0[0] + 3*u**2*t*p1[0] + 3*u*t**2*p2[0] + t**3*p3[0]
    y = u**3*p0[1] + 3*u**2*t*p1[1] + 3*u*t**2*p2[1] + t**3*p3[1]
    return (x, y)


def ease_out_cubic(k):
    return 1 - (1 - k) ** 3


def ease_out_quad(k):
    return 1 - (1 - k) ** 2


def ease_in_out(k):
    if k < 0.5:
        return 2 * k * k
    return 1 - ((-2 * k + 2) ** 2) / 2

# ============================================================
# 背景：星点（极淡）
# ============================================================
class Star:
    __slots__ = ('x', 'y', 'r', 'a', 'ph', 'sp')
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.r = random.uniform(0.4, 1.6)
        self.a = random.uniform(60, 200)
        self.ph = random.uniform(0, math.pi * 2)
        self.sp = random.uniform(0.02, 0.06)
    def update(self):
        self.ph += self.sp
    def draw(self, painter):
        k = 0.5 + 0.5 * math.sin(self.ph)
        a = int(self.a * (0.4 + 0.6 * k))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 240, 250, a))
        painter.drawEllipse(int(self.x - self.r), int(self.y - self.r),
                            int(self.r * 2), int(self.r * 2))

# ============================================================
# 阶段一：双大爱心（沿贝塞尔曲线飞出 + 光晕 + 拖尾）
# ============================================================
class BigFlyingHeart:
    def __init__(self, w, h, color, size, start_side, delay=0):
        self.W, self.H = w, h
        self.color = color
        self.size = size
        self.delay = delay
        self.t = 0
        self.alive = True
        self.gone = False
        # 起始 / 终止：分别从左/右下角 → 中心
        cx, cy = w / 2, h / 2
        if start_side == 'left':
            self.p0 = (-size * 2, h * 0.55)
            self.p3 = (cx, cy)
        else:
            self.p0 = (w + size * 2, h * 0.45)
            self.p3 = (cx, cy)
        # 控制点：带优雅弧度
        if start_side == 'left':
            self.p1 = (w * 0.20, h * 0.15)
            self.p2 = (w * 0.40, cy)
        else:
            self.p1 = (w * 0.80, h * 0.85)
            self.p2 = (w * 0.60, cy)
        # 当前位置 & 拖尾
        self.x, self.y = self.p0
        self.trail = []  # (x, y, alpha)
        self.rot = random.uniform(-15, 15)
        self.rot_speed = random.uniform(-0.3, 0.3)
        self.pulse = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.06, 0.12)

    def update(self):
        if self.delay > 0:
            self.delay -= 1
            return
        self.t += 1
        # 缓动 0→1 飞向中心
        dur = 90
        k = min(1.0, self.t / dur)
        k_e = ease_out_cubic(k)
        # 飞入过程只占 80%，剩余时间做轻微呼吸
        if k < 0.85:
            px, py = bezier_point(self.p0, self.p1, self.p2, self.p3, k_e)
            self.x, self.y = px, py
            # 拖尾
            self.trail.append((self.x, self.y, 220))
            if len(self.trail) > 22:
                self.trail.pop(0)
        else:
            # 在中心附近微微浮动
            kk = (k - 0.85) / 0.15
            cx, cy = self.W / 2, self.H / 2
            ox = math.sin(self.pulse) * 8
            oy = math.cos(self.pulse * 1.3) * 6
            self.x, self.y = cx + ox, cy + oy
        # 拖尾衰减
        new_trail = []
        for (tx, ty, ta) in self.trail:
            ta -= 14
            if ta > 0:
                new_trail.append((tx, ty, ta))
        self.trail = new_trail
        self.rot += self.rot_speed
        self.pulse += self.pulse_speed

    def draw(self, painter):
        # 拖尾（光点）
        for (tx, ty, ta) in self.trail:
            r = self.size * 0.18
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(*self.color, max(0, ta // 3)))
            painter.drawEllipse(int(tx - r), int(ty - r),
                                int(r * 2), int(r * 2))
        # 大光晕
        s = self.size * (1.0 + 0.05 * math.sin(self.pulse * 1.5))
        glow = QRadialGradient(self.x, self.y, s * 2.2)
        glow.setColorAt(0, QColor(*self.color, 90))
        glow.setColorAt(0.4, QColor(*self.color, 50))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(int(self.x - s * 2.2), int(self.y - s * 2.2),
                            int(s * 4.4), int(s * 4.4))
        # 爱心本体
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rot)
        # 描边 + 内填
        path = heart_path(0, 0, s)
        painter.setBrush(QColor(*self.color, 235))
        painter.setPen(QPen(QColor(255, 255, 255, 200), 3))
        painter.drawPath(path)
        # 高光
        hl = QRadialGradient(-s * 0.25, -s * 0.2, s * 0.5)
        hl.setColorAt(0, QColor(255, 255, 255, 180))
        hl.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(hl)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(-s * 0.55), int(-s * 0.45),
                            int(s * 0.7), int(s * 0.5))
        painter.restore()

# ============================================================
# 阶段二：母爱心（向下飘落，沿途洒小爱心）
# ============================================================
class MotherHeart:
    def __init__(self, w, h, x):
        self.W, self.H = w, h
        self.size = random.uniform(36, 56)
        self.x = x
        self.y = -self.size - random.uniform(0, 80)
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(1.6, 2.8)
        self.wobble = random.uniform(0, math.pi * 2)
        self.color = random.choice(HEART_COLORS)
        self.alpha = 0
        self.alive = True
        # 控制沿途洒心
        self.spawn_cooldown = random.randint(6, 14)
        self.children = []  # 自身沿途洒下的小爱心
        # 母爱心的拖尾点
        self.trail = []

    def update(self):
        self.wobble += 0.04
        self.x += self.vx + math.sin(self.wobble) * 0.6
        self.y += self.vy
        self.alpha = min(255, self.alpha + 6)
        # 拖尾
        self.trail.append((self.x, self.y, 200))
        if len(self.trail) > 14:
            self.trail.pop(0)
        new_trail = []
        for (tx, ty, ta) in self.trail:
            ta -= 18
            if ta > 0:
                new_trail.append((tx, ty, ta))
        self.trail = new_trail
        # 洒小爱心
        self.spawn_cooldown -= 1
        if self.spawn_cooldown <= 0 and self.y < self.H * 0.85:
            self.children.append(ChildHeart(self.x, self.y))
            self.spawn_cooldown = random.randint(4, 9)
        # 飞离底部
        if self.y > self.H + self.size:
            self.alive = False

    def draw(self, painter):
        # 拖尾
        for (tx, ty, ta) in self.trail:
            r = self.size * 0.12
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(*self.color, max(0, ta // 3)))
            painter.drawEllipse(int(tx - r), int(ty - r), int(r * 2), int(r * 2))
        # 光晕
        glow = QRadialGradient(self.x, self.y, self.size * 2.0)
        glow.setColorAt(0, QColor(*self.color, 100))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(int(self.x - self.size * 2), int(self.y - self.size * 2),
                            int(self.size * 4), int(self.size * 4))
        # 爱心
        painter.save()
        painter.translate(self.x, self.y)
        path = heart_path(0, 0, self.size)
        painter.setBrush(QColor(*self.color, self.alpha))
        painter.setPen(QPen(QColor(255, 255, 255, min(255, self.alpha // 2)), 1.5))
        painter.drawPath(path)
        painter.restore()


class ChildHeart:
    """由母爱心洒下的小爱心，带闪烁 / 拖尾 / 重力"""
    def __init__(self, x, y):
        self.x = x + random.uniform(-6, 6)
        self.y = y + random.uniform(0, 8)
        self.size = random.uniform(8, 18)
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(0.4, 1.6)  # 向下
        self.color = random.choice(HEART_COLORS + [GOLD, ROSE])
        self.alpha = 230
        self.rot = random.uniform(-30, 30)
        self.rot_speed = random.uniform(-0.8, 0.8)
        self.wobble = random.uniform(0, math.pi * 2)
        self.trail = []
        self.alive = True
        self.twinkle = random.uniform(0, math.pi * 2)

    def update(self):
        self.wobble += 0.06
        self.twinkle += 0.12
        self.vy += 0.015  # 轻微重力
        self.vy = min(self.vy, 2.6)
        self.x += self.vx + math.sin(self.wobble) * 0.4
        self.y += self.vy
        self.rot += self.rot_speed
        # 闪烁
        tw = 0.6 + 0.4 * math.sin(self.twinkle)
        self.alpha = max(0, min(255, int(230 * tw)))
        # 拖尾
        self.trail.append((self.x, self.y, 180))
        if len(self.trail) > 6:
            self.trail.pop(0)
        new_trail = []
        for (tx, ty, ta) in self.trail:
            ta -= 30
            if ta > 0:
                new_trail.append((tx, ty, ta))
        self.trail = new_trail
        if self.y > self.H_parent:
            self.alive = False

    def bind_size(self, W, H):
        self.W_parent = W
        self.H_parent = H

    def draw(self, painter):
        for (tx, ty, ta) in self.trail:
            r = self.size * 0.5
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(*self.color, max(0, ta // 3)))
            painter.drawEllipse(int(tx - r), int(ty - r), int(r * 2), int(r * 2))
        if self.alpha <= 0:
            return
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rot)
        path = heart_path(0, 0, self.size)
        painter.setBrush(QColor(*self.color, self.alpha))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        painter.restore()

# ============================================================
# 阶段三/四：自由飞行的爱心（铺满 + 汇聚）
# ============================================================
class FreeHeart:
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.size = random.uniform(20, 50)
        self.color = random.choice(HEART_COLORS)
        self.alpha = 0
        self.rot = random.uniform(-25, 25)
        self.rot_speed = random.uniform(-0.4, 0.4)
        self.pulse = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.05, 0.10)
        self.visible = False
        self._init_fly()

    def _init_fly(self):
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
        self.fly_delay = random.randint(0, 30)

    def start_gather(self, tx, ty):
        self.tx, self.ty = tx, ty
        if not hasattr(self, '_gx'):
            self._gx, self._gy = self.x, self.y

    def update_fly(self):
        if self.fly_delay > 0:
            self.fly_delay -= 1
            return
        self.visible = True
        self.x += (self.tx - self.x) * 0.10
        self.y += (self.ty - self.y) * 0.10
        self.alpha = min(255, self.alpha + 8)
        if random.random() < 0.05:
            self.tx += random.uniform(-0.6, 0.6)
            self.ty += random.uniform(-0.6, 0.6)
            self.tx = max(self.size, min(self.W - self.size, self.tx))
            self.ty = max(self.size, min(self.H - self.size, self.ty))
        self.rot += self.rot_speed

    def update_drift(self):
        """铺满阶段自由漂浮 + 微微脉动"""
        if random.random() < 0.08:
            self.tx += random.uniform(-0.6, 0.6)
            self.ty += random.uniform(-0.6, 0.6)
            self.tx = max(self.size, min(self.W - self.size, self.tx))
            self.ty = max(self.size, min(self.H - self.size, self.ty))
        self.x += (self.tx - self.x) * 0.05
        self.y += (self.ty - self.y) * 0.05
        self.pulse += self.pulse_speed
        self.alpha = int(200 + 50 * math.sin(self.pulse))
        self.rot += self.rot_speed

    def update_gather(self, t, dur):
        k = min(1.0, t / dur)
        k = ease_out_quad(k)
        # 阶段四前期：先慢后快（吸聚感）
        kk = 1 - (1 - k) ** 2
        # 90% 之前纯线性吸，10% 时给个加速冲刺
        if k < 0.85:
            k_use = k
        else:
            k_use = k + (1 - k) * 0.0  # 占位
        # 保留起点
        if not hasattr(self, '_gx'):
            self._gx, self._gy = self.x, self.y
        # 后期冲刺
        if k < 0.85:
            kk2 = k
        else:
            kk2 = 0.85 + (1 - 0.85) * ease_in_out((k - 0.85) / 0.15)
        self.x = self._gx + (self.tx - self._gx) * kk2
        self.y = self._gy + (self.ty - self._gy) * kk2
        self.alpha = int(255 * (0.6 + 0.4 * kk2))
        self.rot += self.rot_speed * 0.4

    def update_big(self, t, dur):
        """大爱心阶段：所有采样点一起呼吸"""
        cx, cy = self.W / 2, self.H / 2
        self.pulse += self.pulse_speed
        s = 1.0 + 0.07 * math.sin(self.pulse * 1.5)
        dx, dy = self.tx - cx, self.ty - cy
        self.x = cx + dx * s
        self.y = cy + dy * s
        self.alpha = 255

    def update_explode(self, t, dur):
        k = min(1.0, t / dur)
        cx, cy = self.W / 2, self.H / 2
        dx = self.tx - cx
        dy = self.ty - cy
        d = math.hypot(dx, dy) or 1
        if not hasattr(self, '_ex_v'):
            a = math.atan2(dy, dx) + random.uniform(-0.5, 0.5)
            sp = random.uniform(6, 14)
            self._ex_v = (math.cos(a) * sp, math.sin(a) * sp)
        vx, vy = self._ex_v
        self.x += vx
        self.y += vy
        self.rot += self.rot_speed * 2.2
        self.alpha = int(255 * (1 - k * 0.7))
        self.size *= 0.985

    def draw(self, painter):
        if not self.visible or self.alpha <= 0:
            return
        s = self.size
        a = max(0, min(255, self.alpha))
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rot)
        # 光晕
        glow = QRadialGradient(0, 0, s * 1.8)
        glow.setColorAt(0, QColor(*self.color, min(a // 2, 100)))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(int(-s * 1.8), int(-s * 1.8),
                            int(s * 3.6), int(s * 3.6))
        # 爱心
        path = heart_path(0, 0, s)
        painter.setBrush(QColor(*self.color, a))
        painter.setPen(QPen(QColor(255, 255, 255, min(a // 2, 130)), 1.2))
        painter.drawPath(path)
        painter.restore()

# ============================================================
# 阶段五：粉色泡泡
# ============================================================
class Bubble:
    def __init__(self, w, h, x, y):
        self.W, self.H = w, h
        self.x, self.y = x, y
        self.r = random.uniform(18, 40)
        self.vx = random.uniform(-0.6, 0.6)
        self.vy = random.uniform(-1.6, -0.5)
        self.alpha = 0
        self.alive = True
        self.wobble = random.uniform(0, math.pi * 2)
        self.color = random.choice(BUBBLE_COLORS)
        self.grow = random.uniform(0.2, 0.5)

    def update(self, t, dur):
        k = min(1.0, t / dur)
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
        painter.drawEllipse(int(self.x - self.r), int(self.y - self.r),
                            int(self.r * 2), int(self.r * 2))
        # 高光
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, min(220, self.alpha)))
        painter.drawEllipse(int(self.x - self.r * 0.5), int(self.y - self.r * 0.55),
                            int(self.r * 0.35), int(self.r * 0.25))

# ============================================================
# 阶段五：祝福语
# ============================================================
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
        self.color = random.choice(HEART_COLORS + [(255, 100, 150), (200, 80, 200)])
        self.wobble = random.uniform(0, math.pi * 2)

    def update(self, t, dur):
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
        self.x += (self.tx - self.x) * 0.04
        self.y += (self.ty - self.y) * 0.04
        self.wobble += 0.04
        if t > dur - 60 and self.alpha <= 0:
            self.alive = False

    def draw(self, painter):
        if not self.alive or self.alpha <= 0:
            return
        size = max(12, int(42 * self.scale))
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

# ============================================================
# 唯美元素：飘浮羽毛
# ============================================================
class Feather:
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.x = random.uniform(-100, w + 100)
        self.y = random.uniform(-100, h)
        self.size = random.uniform(14, 26)
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(-0.15, -0.05)
        self.rot = random.uniform(0, 360)
        self.rot_speed = random.uniform(-0.4, 0.4)
        self.alpha = random.randint(40, 90)
        self.wobble = random.uniform(0, math.pi * 2)
        self.color = random.choice([(255, 240, 245), (255, 220, 230),
                                    (255, 200, 220), (255, 250, 240)])

    def update(self):
        self.wobble += 0.02
        self.x += self.vx + math.sin(self.wobble) * 0.4
        self.y += self.vy + math.cos(self.wobble * 0.7) * 0.2
        self.rot += self.rot_speed
        if self.y < -self.size * 2:
            self.y = self.H + self.size
            self.x = random.uniform(-50, self.W + 50)
        if self.x < -self.size * 2: self.x = self.W + self.size
        if self.x > self.W + self.size * 2: self.x = -self.size

    def draw(self, painter):
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rot)
        # 简化羽毛：椭圆 + 中线
        painter.setPen(QPen(QColor(*self.color, self.alpha), 1))
        painter.setBrush(QColor(*self.color, self.alpha // 2))
        painter.drawEllipse(int(-self.size), int(-self.size * 0.4),
                            int(self.size * 2), int(self.size * 0.8))
        painter.setPen(QPen(QColor(255, 255, 255, self.alpha), 1))
        painter.drawLine(0, int(-self.size * 0.4), 0, int(self.size * 0.4))
        painter.restore()

# ============================================================
# 主场景
# ============================================================
class HeartsFinaleOverlay(OverlayWindow):
    def __init__(self):
        super().__init__(title="HeartsFinale")
        # 背景星点
        self.stars = [Star(self.W, self.H) for _ in range(90)]
        # 羽毛
        self.feathers = [Feather(self.W, self.H) for _ in range(8)]

        # 阶段一：双爱心
        self.big_heart_a = BigFlyingHeart(self.W, self.H, (255, 90, 160), 200, 'left', delay=0)
        self.big_heart_b = BigFlyingHeart(self.W, self.H, (255, 200, 230), 130, 'right', delay=18)

        # 阶段二：母爱心
        self.mothers = []
        self.children = []  # 所有母爱心洒出的孩子
        self.rain_spawned = False

        # 阶段三/四：小爱心
        self.fill_hearts = [FreeHeart(self.W, self.H) for _ in range(NUM_FILL_HEARTS)]
        self.phase = P_PAIR
        self.phase_t = 0

        # 阶段五
        self.bubbles = []
        self.blessings = []
        self.explode_flash = 0
        self.big_pulse = 0

        # 初始隐藏 fill hearts
        for h in self.fill_hearts:
            h.visible = False
            h.alpha = 0

    # ----------- 重置 -----------
    def on_regenerate(self):
        self.phase = P_PAIR
        self.phase_t = 0
        self.mothers.clear()
        self.children.clear()
        self.bubbles.clear()
        self.blessings.clear()
        self.rain_spawned = False
        self.explode_flash = 0
        self.big_pulse = 0
        # 重置双爱心
        self.big_heart_a = BigFlyingHeart(self.W, self.H, (255, 90, 160), 200, 'left', delay=0)
        self.big_heart_b = BigFlyingHeart(self.W, self.H, (255, 200, 230), 130, 'right', delay=18)
        # 重置 fill_hearts
        for h in self.fill_hearts:
            h._init_fly()
            h.visible = False
            h.alpha = 0
            for attr in ('_gx', '_gy', '_ex_v'):
                if hasattr(h, attr):
                    delattr(h, attr)

    # ----------- 更新 -----------
    def update_scene(self):
        self.phase_t += 1
        # 通用更新
        for s in self.stars: s.update()
        for f in self.feathers: f.update()

        if self.phase == P_PAIR:
            self.big_heart_a.update()
            self.big_heart_b.update()
            if self.phase_t >= PHASE_PAIR_FLY + PHASE_PAIR_HOLD:
                self.phase = P_RAIN
                self.phase_t = 0
                # 启动母爱心
                for i in range(NUM_MOTHERS):
                    x = self.W * (0.10 + 0.80 * (i / max(1, NUM_MOTHERS - 1)))
                    x += random.uniform(-30, 30)
                    m = MotherHeart(self.W, self.H, x)
                    m.delay = i * 8  # 错峰
                    self.mothers.append(m)

        elif self.phase == P_RAIN:
            for m in self.mothers:
                m.update()
            # 收集 child hearts
            for m in self.mothers:
                for c in m.children:
                    c.bind_size(self.W, self.H)
                    self.children.append(c)
                m.children.clear()
            # 更新孩子
            for c in self.children:
                c.update()
            self.children = [c for c in self.children if c.alive]
            self.mothers = [m for m in self.mothers if m.alive]
            if self.phase_t >= PHASE_RAIN:
                self.phase = P_FILL
                self.phase_t = 0
                # 重置 fill_hearts 准备铺满
                for h in self.fill_hearts:
                    h._init_fly()
                    h.visible = False
                    h.alpha = 0

        elif self.phase == P_FILL:
            for h in self.fill_hearts:
                h.update_fly()
            if self.phase_t >= PHASE_FILL_FLY:
                self.phase = P_FILL_HOLD
                self.phase_t = 0

        elif self.phase == P_FILL_HOLD:
            for h in self.fill_hearts:
                h.update_drift()
            if self.phase_t >= PHASE_FILL_HOLD:
                # 设置汇聚目标
                pts = big_heart_points(len(self.fill_hearts), self.W, self.H, scale=0.32)
                random.shuffle(pts)
                for h, (tx, ty) in zip(self.fill_hearts, pts):
                    h.start_gather(tx, ty)
                self.phase = P_CONVERGE
                self.phase_t = 0

        elif self.phase == P_CONVERGE:
            for h in self.fill_hearts:
                h.update_gather(self.phase_t, PHASE_CONVERGE)
            if self.phase_t >= PHASE_CONVERGE:
                self.phase = P_BIG
                self.phase_t = 0

        elif self.phase == P_BIG:
            self.big_pulse += 1
            for h in self.fill_hearts:
                h.update_big(self.phase_t, PHASE_BIG_HOLD)
            if self.phase_t >= PHASE_BIG_HOLD:
                self.phase = P_EXPLODE
                self.phase_t = 0
                self.explode_flash = 20
                cx, cy = self.W / 2, self.H / 2
                for _ in range(NUM_BUBBLES):
                    a = random.uniform(0, math.pi * 2)
                    r = random.uniform(0, 50)
                    self.bubbles.append(Bubble(self.W, self.H,
                                               cx + math.cos(a) * r,
                                               cy + math.sin(a) * r))

        elif self.phase == P_EXPLODE:
            for h in self.fill_hearts:
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
                # 泡泡变祝福语
                self.blessings.clear()
                random.shuffle(BLESSINGS)
                pool = self.bubbles[:NUM_BLESSINGS] if len(self.bubbles) >= NUM_BLESSINGS else self.bubbles
                for i, b in enumerate(pool):
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
                self.on_regenerate()

    # ----------- 绘制 -----------
    def draw_scene(self, painter: QPainter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1) 深紫/暗红/星空渐变背景
        grad = QLinearGradient(0, 0, 0, self.H)
        grad.setColorAt(0,   QColor(28, 12, 38))    # 顶部深紫
        grad.setColorAt(0.5, QColor(60, 18, 50))    # 中部暗红紫
        grad.setColorAt(1,   QColor(35, 8, 32))     # 底部暗红
        painter.fillRect(0, 0, self.W, self.H, grad)

        # 2) 柔光玫瑰色雾（覆盖整体）
        painter.fillRect(0, 0, self.W, self.H, QColor(160, 40, 80, 22))

        # 3) 星点
        for s in self.stars:
            s.draw(painter)

        # 4) 飘浮羽毛
        for f in self.feathers:
            f.draw(painter)

        # 5) 阶段二：母爱心与孩子
        for m in self.mothers:
            m.draw(painter)
        for c in self.children:
            c.draw(painter)

        # 6) 阶段一的双大爱心（覆盖在普通内容之上，但阶段一之后会自然过渡）
        if self.phase == P_PAIR:
            # 先画背后的 a，再画 b（嵌套效果）
            self.big_heart_a.draw(painter)
            self.big_heart_b.draw(painter)
            # 嵌套光环
            cx, cy = self.W / 2, self.H / 2
            ring_grad = QRadialGradient(cx, cy, 220)
            ring_grad.setColorAt(0, QColor(255, 200, 220, 0))
            ring_grad.setColorAt(0.7, QColor(255, 150, 200, 50))
            ring_grad.setColorAt(1, QColor(255, 150, 200, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(ring_grad)
            painter.drawEllipse(int(cx - 240), int(cy - 240), 480, 480)

        # 7) 阶段三/四/五的小爱心
        for h in sorted(self.fill_hearts, key=lambda x: -x.size):
            h.draw(painter)

        # 8) 阶段四 汇聚中：心形轨迹发光曲线（仅 P_CONVERGE 阶段）
        if self.phase == P_CONVERGE:
            k = self.phase_t / PHASE_CONVERGE
            alpha = int(120 * (1 - k))
            pts = big_heart_points(80, self.W, self.H, scale=0.32)
            path = QPainterPath()
            path.moveTo(*pts[0])
            for p in pts[1:]:
                path.lineTo(*p)
            path.closeSubpath()
            painter.setPen(QPen(QColor(255, 200, 230, alpha), 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

        # 9) 阶段五：泡泡 & 祝福
        for b in self.bubbles:
            b.draw(painter)
        for bl in self.blessings:
            bl.draw(painter)

        # 10) 爆炸瞬间全屏闪光
        if self.explode_flash > 0:
            a = int(140 * self.explode_flash / 20)
            painter.fillRect(0, 0, self.W, self.H, QColor(255, 240, 245, a))

        # 11) 阶段提示
        font = QFont("Microsoft YaHei", 22, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 180))
        painter.drawText(20, 50, f"阶段: {PHASE_NAMES[self.phase]}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HeartsFinaleOverlay()
    win.show()
    sys.exit(app.exec())
