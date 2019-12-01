from __future__ import annotations
from typing import Tuple, Sequence, Dict, Set
import abc
import base
import modules


class Action(abc.ABC):  # modifies a module
    pos: base.Vec2d

    @abc.abstractmethod
    def __init__(self, pos):
        self.pos = pos

    @abc.abstractmethod
    def do(self, mod: modules.Module):
        pass

    @abc.abstractmethod
    def undo(self, mod: modules.Module):
        pass

    def type_test(self, val: Tuple[str, str]) -> bool:
        if val[1] == "bool":
            return val[0] == "False" or val[0] == "True"
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


class changeType(Action):
    target: str
    before: modules.Module

    def __init__(self, pos, target):
        self.target = target
        super().__init__(pos)

    def do(self, mod):
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
    changes: Set[Tuple[str, str]] = dict()
    before = None
    after = None

    def __init__(self, pos, changes):
        self.changes = changes
        super().__init__(pos)

    def do(self, mod: modules.Module) -> modules.Module:
        self.before = mod_props = mod.get_exposed_props()
        for name, change in self.changes:
            if name in mod_props and self.type_test(change):
                mod_props[name] = change
            else:
                return None
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
