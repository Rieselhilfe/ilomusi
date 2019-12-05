from __future__ import annotations
from typing import Tuple, Sequence, Dict, Set
import abc
import tcod
import base
import modules
import pulse
import actions
import editor
import board

# TODO
# 1. Menü States - Oder vielleicht auch nicht
# 2. State fürs Einfügen von Modulen
# 3. State fürs editieren von Modulen
# 4. bessere Commands
# 5. Ton
# 6. mehr module
# 7. fertig


class Engine():
    board: board.Board
    editor: editor.Editor
    bcon_offset: int = 3  # should be multiple of three
    econ_offset: int = 3  # should be multiple of three
    e_ratio: int = 3  # size of fraction of screen of edit_con
    # positions of active modules on board:
    delta: float = 0
    beats: int = 0
    actions: Sequence[Sequence[actions.Action]] = []

    def __init__(self):
        self.e_ratio = base.SCREEN_WIDTH//self.e_ratio - \
            (base.SCREEN_WIDTH // self.e_ratio) % 3
        econ_dim = base.Vec2d(self.e_ratio - self.econ_offset*2,
                              base.SCREEN_HEIGHT - self.econ_offset*2)
        bcon_dim = base.Vec2d(base.SCREEN_WIDTH-self.e_ratio - self.bcon_offset*2,
                              base.SCREEN_HEIGHT - self.bcon_offset*2)
        board_con = tcod.console.Console(bcon_dim.x,
                                         bcon_dim.y)
        editor_con = tcod.console.Console(econ_dim.x,
                                          econ_dim.y)
        self.board = board.Board(board_con, self.e_ratio, bcon_dim)
        self.editor = editor.Editor(editor_con, 0, econ_dim)
        self.editor.update_keymap(self.board.get_prop_at(self.editor.cursor),
                                  self.board.get_name_at(self.editor.cursor))

    def update(self) -> bool:
        # key handling
        for event in tcod.event.get():
            if event.type == "QUIT":
                raise SystemExit()
            if event.type == "KEYUP":
                actions = self.editor.handle_input(event, self.board.dim)
                if actions:
                    self.do_actions(actions)

        self.delta += tcod.sys_get_last_frame_length()
        if self.delta >= base.STEP:
            self.beats += 1
            # moving pulses
            self.board.update(self.beats)
            self.delta = 0

    def render(self):
        self.board.render(self.editor.cursor)
        self.editor.render()
        base.root_console.print(5, 0, "fps: "+str(tcod.sys_get_fps()))

    def do_actions(self, actions: Sequence[actions.Action]):
        staged_actions = []
        for action in actions:
            if action.scope == "Module":
                staged_actions.append(self.board.do_action(action,
                                                           self.editor.cursor))
            elif action.scope == "Editor":
                self.editor = action.do(self.editor, self.board.dim)
                staged_actions.append(action)
            else:
                print("invalid action scope", action.scope)
        self.editor.update_keymap(self.board.get_prop_at(self.editor.cursor),
                                  self.board.get_name_at(self.editor.cursor))
        self.actions.append(staged_actions)


eng = Engine()
