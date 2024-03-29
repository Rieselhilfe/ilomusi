from __future__ import annotations
from typing import Tuple, Sequence, Dict
import tcod
import tcod.event
from random import randint
from collections import namedtuple


# ---tcod init--- #
SCREEN_WIDTH = 192
SCREEN_HEIGHT = 108
LIMIT_FPS = 30
STEP = 0.2

font_path = 'terminal10x10_gs_tc.png'
font_flags = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
tcod.console_set_custom_font(font_path, font_flags)
window_title = 'ilomusi'
fullscreen = True
root_console = tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
                                      window_title, fullscreen,
                                      tcod.RENDERER_SDL2, order="F", vsync=False)
tcod.sys_set_fps(LIMIT_FPS)
# colors: http://roguecentral.org/doryen/data/libtcod/doc/1.5.1/html2/color.html?c=false&cpp=false&cs=false&py=true&lua=false


# character, foreground colour, background colour:
Symbol = Tuple[str, int, int]

Chunk = Tuple[Tuple[Symbol, Symbol, Symbol],
              Tuple[Symbol, Symbol, Symbol],
              Tuple[Symbol, Symbol, Symbol]]

Color = Tuple[int, int, int]


class Vec2d():
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def is_inner(self, vec: Vec2d):
        if self.x < 0 or self.x >= vec.x or \
                self.y < 0 or self.y >= vec.y:
            return False
        else:
            return True

    def crop(self, vec: Vec2d):
        return Vec2d(max(min(vec.x-1, self.x), 0),
                     max(min(vec.y-1, self.y), 0))

    def to_tuple(self):
        return (self.x, self.y)

    def mul(self, n: int):
        return Vec2d(self.x*n, self.y*n)

    def __add__(self, other: Vec2d):
        return Vec2d(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)


DIR_UP = Vec2d(0, -1)
DIR_RIGHT = Vec2d(1, 0)
DIR_DOWN = Vec2d(0, 1)
DIR_LEFT = Vec2d(-1, 0)

prompt = "(ilomusi):> "
underline_char = "="
bar_char = "-"

cols = {
    "outer_bg": tcod.darker_sky,
    "outer_fg": tcod.white,
    "inactive": tcod.darker_gray,
    "bg": tcod.darkest_gray,
    "fg": tcod.white,
    "cursor_bg": tcod.darker_sea,
    "cursor_fg": tcod.black,
    "pulse_bg": tcod.gold,
    "pulse_fg": tcod.black,
    "mirror_fg": tcod.flame,
    "source_fg": tcod.lime,
    "menu_title_fg": tcod.light_flame,
    "menu_bar_fg": tcod.darker_gray,
}

mod_type_keys = "qwertzuiop"
mod_prop_keys = "asdfgyxcvbnm"

sym_char_dict = {
    tcod.event.K_a: "a",
    tcod.event.K_b: "b",
    tcod.event.K_c: "c",
    tcod.event.K_d: "d",
    tcod.event.K_e: "e",
    tcod.event.K_f: "f",
    tcod.event.K_g: "g",
    tcod.event.K_h: "h",
    tcod.event.K_i: "i",
    tcod.event.K_j: "j",
    tcod.event.K_k: "k",
    tcod.event.K_l: "l",
    tcod.event.K_m: "m",
    tcod.event.K_n: "n",
    tcod.event.K_o: "o",
    tcod.event.K_p: "p",
    tcod.event.K_q: "q",
    tcod.event.K_r: "r",
    tcod.event.K_s: "s",
    tcod.event.K_t: "t",
    tcod.event.K_u: "u",
    tcod.event.K_v: "v",
    tcod.event.K_w: "w",
    tcod.event.K_x: "x",
    tcod.event.K_y: "y",
    tcod.event.K_z: "z",
    tcod.event.K_0: "0",
    tcod.event.K_1: "1",
    tcod.event.K_2: "2",
    tcod.event.K_3: "3",
    tcod.event.K_4: "4",
    tcod.event.K_5: "5",
    tcod.event.K_6: "6",
    tcod.event.K_7: "7",
    tcod.event.K_8: "8",
    tcod.event.K_9: "9",
}

char_sym_dict = {
    value: key for key, value in sym_char_dict.items()
}
