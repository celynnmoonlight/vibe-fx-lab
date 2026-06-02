"""颜色工具"""

import random
from shared.config import NEON_COLORS


def random_neon():
    """返回一个随机霓虹色 RGB 元组"""
    return random.choice(NEON_COLORS)


def random_neon_rgba(alpha=255):
    """返回带 alpha 的随机霓虹色"""
    r, g, b = random_neon()
    return (r, g, b, alpha)


def lerp_color(c1, c2, t):
    """线性插值两个颜色"""
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def with_alpha(color, alpha):
    """给 RGB 颜色加上 alpha 通道"""
    return (*color[:3], alpha)
