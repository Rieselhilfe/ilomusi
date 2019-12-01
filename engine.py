from __future__ import annotations
from typing import Tuple, Sequence, Dict, Set
import abc
import tcod
import string
import base
import modules
import pulse
import actions
import editor

# TODO
# 1. Menü States - Oder vielleicht auch nicht
# 2. State fürs Einfügen von Modulen
# 3. State fürs editieren von Modulen
# 4. bessere Commands
# 5. Ton
# 6. mehr module
# 7. fertig


class Engine():
    board: Sequence[Sequence[modules.Module]]
    board_con: 'Console' = None
    editor: Editor = editor.Editor()
    edit_con: 'Console' = None
    b_dimensions: base.Vec2d  # dimensions of board in characters
    bcon_dimensions: base.Vec2d  # " " " in pixels
    bcon_offset: int
    econ_dimensions: base.Vec2d
    econ_offset: int
    econ_inner_offset: int
    e_ratio: int = 3  # size of fraction of screen of edit_con
    cursor: base.Vec2d = base.Vec2d(1, 1)
    pulses: Sequence[pulse.Pulse] = []
    # positions of active modules on board:
    active_modules: Set[Tuple[int, int]] = set()
    delta: float = 0
    beats: int = 0
    actions: Sequence[actions.Action] = []

    def __init__(self):
        self.econ_offset = self.bcon_offset = 3  # should be multiple of three
        self.e_ratio = base.SCREEN_WIDTH//self.e_ratio - \
            (base.SCREEN_WIDTH // self.e_ratio) % 3
        self.econ_dimensions = base.Vec2d(self.e_ratio - self.econ_offset*2,
                                          base.SCREEN_HEIGHT - self.econ_offset*2)
        self.bcon_dimensions = base.Vec2d(base.SCREEN_WIDTH-self.e_ratio - self.bcon_offset*2,
                                          base.SCREEN_HEIGHT - self.bcon_offset*2)
        self.board_con = tcod.console.Console(self.bcon_dimensions.x,
                                              self.bcon_dimensions.y)
        self.edit_con = tcod.console.Console(self.econ_dimensions.x,
                                             self.econ_dimensions.y)
        self.b_dimensions = base.Vec2d(self.bcon_dimensions.x//3,
                                       self.bcon_dimensions.y//3)
        self.econ_inner_offset = 1

        self.board_con.default_bg = self.edit_con.default_bg = base.cols["bg"]
        self.board_con.default_fg = self.edit_con.default_fg = base.cols["fg"]

        self.board = []
        for x in range(self.b_dimensions.x):
            new_column = []
            for y in range(self.b_dimensions.y):
                new_column.append(modules.Empty(base.Vec2d(x, y)))
            self.board.append(new_column)

    def update(self) -> bool:
        # key handling
        for event in tcod.event.get():
            if event.type == "QUIT":
                raise SystemExit()
            if event.type == "KEYUP":
                if event.sym == tcod.event.K_ESCAPE:
                    raise SystemExit()
                if event.sym == tcod.event.K_DOWN:
                    mv_vec = base.Vec2d(0, 1)
                    self.cursor = self.cursor + mv_vec
                    self.cursor = self.cursor.crop(self.b_dimensions)
                elif event.sym == tcod.event.K_UP:
                    mv_vec = base.Vec2d(0, -1)
                    self.cursor = self.cursor + mv_vec
                    self.cursor = self.cursor.crop(self.b_dimensions)
                elif event.sym == tcod.event.K_LEFT:
                    mv_vec = base.Vec2d(-1, 0)
                    self.cursor = self.cursor + mv_vec
                    self.cursor = self.cursor.crop(self.b_dimensions)
                elif event.sym == tcod.event.K_RIGHT:
                    mv_vec = base.Vec2d(1, 0)
                    self.cursor = self.cursor + mv_vec
                    self.cursor = self.cursor.crop(self.b_dimensions)
                else:
                    action = self.editor.handle_input(event, self.cursor)
                    if action:
                        self.do_action(action)

        self.delta += tcod.sys_get_last_frame_length()
        if self.delta >= base.STEP:
            self.beats += 1
            # moving pulses
            new_pulses = []
            for p in self.pulses:
                nnps = self.board[p.pos.x][p.pos.y].on_pulse(p)
                nnps = [p for p in nnps if p.pos.is_inner(self.b_dimensions)]
                new_pulses += nnps

            # sources
            for x, y in self.active_modules:
                new_pulses += self.board[x][y].on_beat(self.beats)

            self.pulses = new_pulses
            self.delta = 0

    def render(self):
        # render modules, cursor, pulses
        pulse_positions = [p.pos.to_tuple() for p in self.pulses]
        self.board_con.clear()
        for x, column in enumerate(self.board):
            for y, module in enumerate(column):
                if (x, y) in pulse_positions:
                    self.draw_chunk(module.get_chunk(),
                                    module.pos, bg=base.cols["pulse_bg"],
                                    fg=base.cols["pulse_fg"])
                elif self.cursor == base.Vec2d(x, y):
                    self.draw_chunk(module.get_chunk(),
                                    module.pos, bg=base.cols["cursor_bg"],
                                    fg=base.cols["cursor_fg"])
                else:
                    self.draw_chunk(module.get_chunk(), module.pos)
        self.board_con.blit(base.root_console,
                            self.bcon_offset + self.e_ratio, self.bcon_offset)

        # render code
        self.edit_con.clear()
        e_text = "\n".join(self.editor.text)
        self.edit_con.print(self.econ_inner_offset,
                            self.econ_inner_offset, e_text)
        self.edit_con.blit(base.root_console,
                           self.econ_offset, self.econ_offset)

    def draw_chunk(self, chunk: base.Chunk, pos: base.Vec2d,
                   fg: base.Color = None, bg: base.Color = None):
        render_pos = pos.mul(3)
        if not chunk:
            self.board_con.default_fg = self.board_con.default_bg = self.board_con.default_bg if not bg else bg
            self.board_con.draw_frame(render_pos.x, render_pos.y, 3, 3,
                                      fg=self.board_con.default_fg,
                                      bg=self.board_con.default_bg, clear=True)
            self.board_con.default_fg = base.cols["inactive"] if not fg else fg
            tcod.console_put_char(self.board_con, render_pos.x+1,
                                  render_pos.y+1, "=", tcod.BKGND_SET)
            self.board_con.default_fg = base.cols["fg"]
            self.board_con.default_bg = base.cols["bg"]
            return

        self.board_con.default_fg = chunk[1][1][1] if not fg else fg
        self.board_con.default_bg = chunk[1][1][2] if not bg else bg
        self.board_con.draw_frame(render_pos.x, render_pos.y, 3, 3,
                                  fg=self.board_con.default_fg,
                                  bg=self.board_con.default_bg)
        for x in range(3):
            for y in range(3):
                if chunk[x][y]:
                    self.board_con.default_fg = chunk[x][y][1] if not fg else fg
                    tcod.console_put_char(self.board_con, render_pos.x+x,
                                          render_pos.y+y,
                                          chunk[x][y][0], tcod.BKGND_SET)
                    self.board_con.default_fg = base.cols["fg"]
        self.board_con.default_bg = base.cols["bg"]

    def do_action(self, action: actions.Action):
        pos = action.pos
        if self.board[pos.x][pos.y].active:
            self.active_modules.remove((pos.x, pos.y))
        self.board[pos.x][pos.y] = action.do(self.board[pos.x][pos.y])
        if self.board[pos.x][pos.y].active:
            self.active_modules.add((pos.x, pos.y))
        self.actions.append(action)


eng = Engine()
