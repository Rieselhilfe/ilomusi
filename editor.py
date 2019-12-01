from __future__ import annotations
from typing import Tuple, Sequence, Dict, Set
import tcod
import abc
import base
import modules
import actions


class EState():
    keytable = {
        "changeTypeToSource": tcod.event.K_s,
        "changeTypeToMirror": tcod.event.K_m,
        "changeTypeToEmpty": tcod.event.K_e
    }


class Editor():  # input handler and menu
    text: Sequence[str] = ["system commands",
                           "---------------",
                           "esc - exit ilokalama",
                           ". - save board (TODO)",
                           ", - load board (TODO)", ""]
    commandline: str = ""
    keytable = {
        "changeTypeToSource": tcod.event.K_s,
        "changeTypeToMirror": tcod.event.K_m,
        "changeTypeToEmpty": tcod.event.K_e
    }
    state: EState = None

    def handle_input(self, event, cursor) -> actions.Action:
        if event.sym == self.keytable["changeTypeToSource"]:
            return actions.changeType(cursor, "Source")
        elif event.sym == self.keytable["changeTypeToMirror"]:
            return actions.changeType(cursor, "Mirror")
        elif event.sym == self.keytable["changeTypeToEmpty"]:
            return actions.changeType(cursor, "Empty")
        else:
            return None
