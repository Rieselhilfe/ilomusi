from __future__ import annotations
from typing import Tuple, Sequence, Dict, Set
import abc
import base
import modules


class Action(abc.ABC):  # modifies a module
    scope: str  # Module or Editor
    pos: base.Vec2d

    @abc.abstractmethod
    def do(self, other):
        pass

    @abc.abstractmethod
    def undo(self, other):
        pass


class changeType(Action):
    scope: str = "Module"
    target: str
    before: modules.Module

    def __init__(self, target):
        self.target = target

    def do(self, mod: modules.Module, pos: base.Vec2d) -> modules.Module:
        self.pos = pos
        self.before = mod
        return modules.name_to_module(self.target, self.pos)

    def undo(self, mod):
        if mod.name.strip().lower() == self.target.strip().lower():
            return self.before
        else:
            print("tried to undo, but target was", self.target,
                  "while the current module is", mod.name)
            return None


class changeProperty(Action):
    scope: str = "Module"
    changes: [Tuple[str, str]] = dict()
    before = None
    after = None

    def __init__(self, changes):
        self.changes = changes

    def do(self, mod: modules.Module, pos: base.Vec2d) -> modules.Module:
        self.pos = pos
        self.before = mod_props = mod.get_exposed_props()
        for name, change in self.changes.items():
            if name in mod_props and self.type_test(change):
                mod_props[name] = change
            else:
                return mod
        self.after = mod_props
        mod.set_exposed_props(mod_props)
        return mod

    def undo(self, mod: modules.Module):
        props = mod.get_exposed_props()
        if self.before and self.before.keys() == props.keys() \
                and props() == self.after:
            mod.set_exposed_props(self.before)
            return mod
        else:
            print("tried to undo, but the target props are",
                  self.before, "while the current are", props)
            return None

    def type_test(self, val: Tuple[str, str]) -> bool:
        if val[1] == "bool":
            return val[0] == "f" or val[0] == "t"
        elif val[1] == "int":
            return val[0].isdigit()
        elif val[1] == "char":
            return len(val[0]) == 1
        elif val[1] == "color":
            return len(val[0]) > 2 and \
                tuple(x.strip().isdigit() for x
                      in val[0][1:-1].split(",")) == (True, True, True)
        else:
            print("invalid type:", val[1])


class moveCursor(Action):
    scope: str = "Editor"
    direction: base.Vec2d

    def __init__(self, direction: base.Vec2d):
        self.direction = direction

    def do(self, ed: 'editor.Editor', boundaries: int):
        ed.move_cursor(self.direction, boundaries)
        return ed

    def undo(self, ed):
        return ed
