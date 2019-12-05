from __future__ import annotations
from typing import Tuple, Sequence, Dict, Set
import abc
import tcod
import base
import modules
import pulse
import actions


class Board():
    modules: Sequence[Sequence[modules.Module]]
    con: tcod.console.Console = None
    con_pos: base.Vec2d
    con_dim: base.Vec2d  # dimensions in characters
    con_offset: base.Vec2d = 3
    dim: base.Vec2d  # dimensions in blocks
    pulses: Sequence[pulse.Pulse] = []
    active_modules: Set[Tuple[int, int]] = set()

    def __init__(self, con: tcod.console.Console, con_pos: base.Vec2d, con_dim: base.Vec2d):
        self.con = con
        self.con.default_bg = base.cols["bg"]
        self.con.default_fg = base.cols["fg"]
        self.con_dim = con_dim
        self.con_pos = con_pos
        self.dim = base.Vec2d(self.con_dim.x//3,
                              self.con_dim.y//3)

        self.modules = []
        for x in range(self.dim.x):
            new_column = []
            for y in range(self.dim.y):
                new_column.append(modules.Empty(base.Vec2d(x, y)))
            self.modules.append(new_column)

    def update(self, beats: int):
        new_pulses = []
        for p in self.pulses:
            nnps = self.modules[p.pos.x][p.pos.y].on_pulse(p)
            nnps = [p for p in nnps if p.pos.is_inner(self.dim)
                    and p not in new_pulses]
            new_pulses += nnps

        # sources
        for x, y in self.active_modules:
            new_pulses += self.modules[x][y].on_beat(beats)

        self.pulses = new_pulses

    def render(self, cursor):

        def draw_chunk(chunk: base.Chunk, pos: base.Vec2d,
                       fg: base.Color = None, bg: base.Color = None):
            render_pos = pos.mul(3)
            if not chunk:
                self.con.default_fg = self.con.default_bg = self.con.default_bg if not bg else bg
                self.con.draw_frame(render_pos.x, render_pos.y, 3, 3,
                                    fg=self.con.default_fg,
                                    bg=self.con.default_bg, clear=True)
                self.con.default_fg = base.cols["inactive"] if not fg else fg
                tcod.console_put_char(self.con, render_pos.x+1,
                                      render_pos.y+1, "=", tcod.BKGND_SET)
                self.con.default_fg = base.cols["fg"]
                self.con.default_bg = base.cols["bg"]
                return

            self.con.default_fg = chunk[1][1][1] if not fg else fg
            self.con.default_bg = chunk[1][1][2] if not bg else bg
            self.con.draw_frame(render_pos.x, render_pos.y, 3, 3,
                                fg=self.con.default_fg,
                                bg=self.con.default_bg)
            for x in range(3):
                for y in range(3):
                    if chunk[x][y]:
                        self.con.default_fg = chunk[x][y][1] if not fg else fg
                        tcod.console_put_char(self.con, render_pos.x+x,
                                              render_pos.y+y,
                                              chunk[x][y][0], tcod.BKGND_SET)
                        self.con.default_fg = base.cols["fg"]
            self.con.default_bg = base.cols["bg"]

        pulse_positions = [p.pos.to_tuple() for p in self.pulses]
        self.con.clear()
        for x, column in enumerate(self.modules):
            for y, module in enumerate(column):
                if cursor == base.Vec2d(x, y):
                    draw_chunk(module.get_chunk(),
                               module.pos, bg=base.cols["cursor_bg"],
                               fg=base.cols["cursor_fg"])
                elif (x, y) in pulse_positions:
                    draw_chunk(module.get_chunk(),
                               module.pos, bg=base.cols["pulse_bg"],
                               fg=base.cols["pulse_fg"])
                else:
                    draw_chunk(module.get_chunk(), module.pos)
        self.con.blit(base.root_console,
                      self.con_pos + self.con_offset, self.con_offset)

    def do_action(self, action: actions.Action, pos: base.Vec2d) -> actions.Action:
        if self.modules[pos.x][pos.y].active:
            self.active_modules.remove((pos.x, pos.y))

        self.modules[pos.x][pos.y] = action.do(self.modules[pos.x][pos.y], pos)

        if self.modules[pos.x][pos.y].active:
            self.active_modules.add((pos.x, pos.y))

        return action

    def get_prop_at(self, pos: base.Vec2d):
        return self.modules[pos.x][pos.y].get_exposed_props()

    def get_name_at(self, pos: base.Vec2d):
        return self.modules[pos.x][pos.y].name
