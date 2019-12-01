from __future__ import annotations
from typing import Tuple, Sequence, Dict
import base


class Pulse():
    pos: base.Vec2d
    direction: base.Vec2d

    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction

    def move(self):
        self.pos = self.pos + self.direction
