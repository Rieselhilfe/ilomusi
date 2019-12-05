from __future__ import annotations
from typing import Tuple, Sequence, Dict, Set
import tcod
import abc
import base
import modules
import actions


class Editor():  # input handler and menu
    con: 'Console' = None
    con_pos: base.Vec2d
    con_dim: base.Vec2d
    con_offset: int = 3
    con_inner_offset: int = 1

    cursor: base.Vec2d = base.Vec2d(0, 0)
    topmenu_text: Sequence[Sequence[str]] = [
        ["system commands (instant)",
         "esc - exit ilokalama",
         ". - save board (TODO)",
         ", - load board (TODO)"],
        ["generic commands",
         "[number]* - repeat commands n times"],
        ["module commands"]+[
            base.mod_type_keys[i]+" - change module type to "+name
            for i, name in enumerate(modules.names)
        ],
        #  base.mod_type_keys[3]+" - change module type to output"],
        []
    ]
    submenu_text: Sequence[Sequence[str]] = [
        ["system commands (instant)",
         "esc - exit submenu",
         ". - save board (TODO)",
         ", - load board (TODO)"],
        []
    ]
    commandline: str = ""

    keytable = {
        **{
            base.mod_type_keys[i]: actions.changeType(name)
            for i, name in enumerate(modules.names)
        },
        # base.mod_type_keys[3]: actions.changeType("Output"),
        "h": actions.moveCursor(base.DIR_LEFT),
        "j": actions.moveCursor(base.DIR_DOWN),
        "k": actions.moveCursor(base.DIR_UP),
        "l": actions.moveCursor(base.DIR_RIGHT)
    }
    mod_keytable = {}
    focused_property: str = None

    def __init__(self, con: tcod.console.Console, con_pos: base.Vec2d, con_dim: base.Vec2d):
        self.con = con
        self.con.default_bg = base.cols["bg"]
        self.con.default_fg = base.cols["fg"]
        self.con_dim = con_dim
        self.con_pos = con_pos

    def render(self):
        def bar(ch):
            return "".join([ch for x
                            in range(self.con_dim.x//2)])

        def eprint(txt, fg, line_num):
            self.con.print(self.con_inner_offset,
                           self.con_inner_offset+line_num, txt,
                           fg=fg)

        def menu_text(blocks):
            self.con.clear()
            line_num = 0
            for block in blocks:
                if not block:
                    continue
                eprint(block[0], base.cols["menu_title_fg"], line_num)
                line_num += 1
                eprint(bar(base.underline_char),
                       base.cols["menu_bar_fg"], line_num)
                line_num += 1
                for line in block[1:]:
                    eprint(line, base.cols["fg"], line_num)
                    line_num += 1
                eprint(bar(base.bar_char),
                       base.cols["menu_bar_fg"], line_num)
                line_num += 2

        if not self.focused_property:
            menu_text(self.topmenu_text)
        else:
            menu_text(self.submenu_text)

        self.con.print(self.con_inner_offset,
                       self.con_dim.y-self.con_inner_offset-2,
                       base.prompt+self.commandline)
        self.con.blit(base.root_console,
                      self.con_pos + self.con_offset, self.con_offset)

    def handle_input(self, event, b_dimensions) -> actions.Action:

        if event.sym == tcod.event.K_ESCAPE:
            if not self.focused_property:
                raise SystemExit()
            else:
                self.focused_property = None
        if event.sym == tcod.event.K_DOWN:
            self.focused_property = None
            return [actions.moveCursor(base.DIR_DOWN)]
        elif event.sym == tcod.event.K_UP:
            self.focused_property = None
            return [actions.moveCursor(base.DIR_UP)]
        elif event.sym == tcod.event.K_LEFT:
            self.focused_property = None
            return [actions.moveCursor(base.DIR_LEFT)]
        elif event.sym == tcod.event.K_RIGHT:
            self.focused_property = None
            return [actions.moveCursor(base.DIR_RIGHT)]
        elif event.sym == tcod.event.K_RETURN:
            cmd = self.commandline
            self.commandline = ""
            if cmd:
                return self.exec_command(cmd)
        elif event.sym == tcod.event.K_BACKSPACE:
            if self.commandline:
                self.commandline = self.commandline[:-1]
        else:
            if event.sym in base.sym_char_dict:
                self.commandline += base.sym_char_dict[event.sym]
            else:
                return None
        return None

    def update_keymap(self, mod_props, mod_name: str):
        if mod_props and not self.focused_property:
            self.mod_keytable = {}
            menu_entry = ["property commands: "+mod_name]
            for i, d in enumerate(mod_props.items()):
                name, prop = d
                key = base.mod_prop_keys[i]
                self.mod_keytable[key] = (name, prop)
                menu_entry.append(key+" - "+prop[2])
        elif not mod_props:
            menu_entry = []
        else:
            self.focused_property = None
            return
        self.topmenu_text[3] = menu_entry

    def exec_command(self, cmd: str) -> Sequence[actions.Action]:
        if self.focused_property:
            changes = {
                self.focused_property[0]: (cmd, *self.focused_property[1][1:])
            }
            self.focused_property = None
            return [actions.changeProperty(changes)]
        elif cmd[0] in self.mod_keytable:
            self.focused_property = self.mod_keytable[cmd[0]]
            if len(cmd) == 1:
                self.submenu_text[1] = [
                    self.mod_keytable[cmd][1][2],
                    "type: "+self.mod_keytable[cmd][1][1],
                    "current value: "+self.mod_keytable[cmd][1][0]
                ]
                return None
            else:
                changes = {
                    self.focused_property[0]: (
                        cmd[1:], *self.focused_property[1][1:])
                }
                self.focused_property = None
                return [actions.changeProperty(changes)]

        multiplier = 1
        ret_actions = []
        staged_actions = []
        block = True
        for c in cmd:
            if c.isnumeric():
                if block:
                    ret_actions += staged_actions * multiplier
                    multiplier = int(c)
                    staged_actions = []
                    block = False
                else:
                    multiplier = multiplier*10 + int(c)
            else:
                if c in self.keytable:
                    action = self.keytable[c]
                    staged_actions.append(action)
                else:
                    print("invalid char:", c)
                    return None
        ret_actions += staged_actions * multiplier
        return ret_actions

    def set_focused_property(self, char):
        pass

    def move_cursor(self, mvmnt: base.Vec2d, boundaries: base.Vec2d):
        self.cursor = self.cursor + mvmnt
        self.cursor = self.cursor.crop(boundaries)
