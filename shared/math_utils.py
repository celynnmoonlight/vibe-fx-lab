"""数学工具"""

import math
import numpy as np


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def angle_between(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def rotate_point(x, y, cx, cy, angle):
    """绕 (cx, cy) 旋转点 (x, y)"""
    dx, dy = x - cx, y - cy
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a


def points_on_circle(cx, cy, r, n, offset_angle=0):
    """在圆上均匀取 n 个点"""
    pts = []
    for i in range(n):
        a = offset_angle + 2 * math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def noise_2d(x, y, seed=0):
    """简易 2D 哈希噪声"""
    n = int(x * 374761393 + y * 668265263 + seed)
    n = (n ^ (n >> 13)) * 1274126177
    return (n & 0x7fffffff) / 0x7fffffff
