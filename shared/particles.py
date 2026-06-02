"""粒子系统基类"""

import math
import random
import numpy as np


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'size', 'color', 'alpha')

    def __init__(self, x, y, vx, vy, life, size, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.alpha = 255

    def update(self, dt=1.0):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        ratio = max(0, self.life / self.max_life)
        self.alpha = int(255 * ratio)

    @property
    def alive(self):
        return self.life > 0


class ParticleSystem:
    def __init__(self, max_particles=500):
        self.particles: list[Particle] = []
        self.max_particles = max_particles

    def emit(self, x, y, count=1, speed_range=(0.5, 3.0),
             life_range=(30, 120), size_range=(1, 4), color=(0, 255, 255)):
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(*life_range)
            size = random.uniform(*size_range)
            self.particles.append(Particle(x, y, vx, vy, life, size, color))

    def update(self, dt=1.0):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def clear(self):
        self.particles.clear()

    @property
    def count(self):
        return len(self.particles)
