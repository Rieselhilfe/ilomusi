from __future__ import annotations
from typing import Tuple, Sequence, Dict, Set
import abc
import base
import pulse
import tcod
import time

import rtmidi


class Module(abc.ABC):
    name: str
    active: bool = False  # whether it can send out pulses on its own
    # the central symbol
    symbol: base.Symbol = (":", base.cols["inactive"], base.cols["bg"])
    pos: base.Vec2d  # position on the borad (x,y)
    col_fg: int  # fg color of the central symbol
    col_bg: int  # bg color of the central symbol

    def __init__(self, pos: base.Vec2d, symbol: base.Symbol = None):
        self.pos = pos
        if symbol:
            self.symbol = symbol

    def get_chunk(self) -> base.Chunk:
        return (tuple(None for x in range(3)),
                (None, self.symbol, None),
                tuple(None for x in range(3)))
        # (tuple(None for x in range(3)),
        #  (None, self.symbol, None),
        #  tuple(None for x in range(3)))

    def on_pulse(self, p: pulse.Pulse) -> Sequence[pulse.Pulse]:
        p.move()
        return [p]

    def on_beat(self, beats) -> Sequence[pulse.Pulse]:
        return []

    @abc.abstractmethod
    # props = dict of (value, type, description)
    def get_exposed_props(self) -> Dict[str, Tuple[str, str, str]]:
        return None

    @abc.abstractmethod
    def set_exposed_props(self, props: Dict[str, Tuple[str, str, str]]):
        pass


class Empty(Module):
    name: str = "Empty"
    active: bool = False

    def get_chunk(self):
        return None

    def get_exposed_props(self):
        return super().get_exposed_props()

    def set_exposed_props(self, props):
        pass


class Spreader(Module):
    name: str = "Spreader"
    active: bool = False
    symbol: base.Symbol = ("]", base.cols["mirror_fg"], base.cols["bg"])

    inp: Sequence[base.Vec2d] = [base.DIR_DOWN, base.DIR_UP,
                                 base.DIR_LEFT, base.DIR_RIGHT]
    outp: Sequence[base.Vec2d] = [base.DIR_RIGHT]

    def on_pulse(self, p):
        if p.direction in self.inp:
            out_pulses = []
            for o in self.outp:
                np = pulse.Pulse(p.pos, o)
                np.move()
                out_pulses.append(np)
        return out_pulses

    def get_exposed_props(self):
        props = {
            "character": (self.symbol[0], "char", "character"),
            "color": (str(self.symbol[1]), "color", "color"),
            "up_is_input": (str(base.DIR_UP in self.inp), "bool",
                            "up is input"),
            "down_is_input": (str(base.DIR_DOWN in self.inp), "bool",
                              "down is input"),
            "left_is_input": (str(base.DIR_LEFT in self.inp), "bool",
                              "left is input"),
            "right_is_input": (str(base.DIR_RIGHT in self.inp), "bool",
                               "right is input"),
            "up_is_output": (str(base.DIR_UP in self.outp), "bool",
                             "up is output"),
            "down_is_output": (str(base.DIR_DOWN in self.outp), "bool",
                               "down is output"),
            "left_is_output": (str(base.DIR_LEFT in self.outp), "bool",
                               "left is output"),
            "right_is_output": (str(base.DIR_RIGHT in self.outp), "bool",
                                "right is output")
        }
        return props

    def set_exposed_props(self, props):
        props = {key: value[0] for key, value in props.items()}
        color = tuple(int(x) for x in props["color"][1:-1].split(","))
        self.symbol = (props["character"], color, self.symbol[2])

        self.inp = []
        self.inp += [base.DIR_UP] if props["up_is_input"] == "t" else []
        self.inp += [base.DIR_DOWN] if props["down_is_input"] == "t" else []
        self.inp += [base.DIR_LEFT] if props["left_is_input"] == "t" else []
        self.inp += [base.DIR_RIGHT] if props["right_is_input"] == "t" else []
        self.outp = []
        self.outp += [base.DIR_UP] if props["up_is_output"] == "t" else []
        self.outp += [base.DIR_DOWN] if props["down_is_output"] == "t" else []
        self.outp += [base.DIR_LEFT] if props["left_is_output"] == "t" else []
        self.outp += [base.DIR_RIGHT] if props["right_is_output"] == "t" else []


class Emitter(Module):
    name: str = "Emitter"
    active: bool = True
    symbol: base.Symbol = ("O", base.cols["source_fg"], base.cols["bg"])

    outp: Sequence[base.Vec2d] = [base.DIR_UP]
    interval: int = 5  # (beats % interval == 0) => pulse
    offset: int = 0  # offset off the interval

    def on_beat(self, beats) -> Sequence[pulse.Pulse]:
        if beats % self.interval - self.offset == 0:
            return [pulse.Pulse(self.pos, o) for o in self.outp]

        return []

    def get_exposed_props(self):
        props = {
            "character": (self.symbol[0], "char", "character"),
            "color": (str(tuple(self.symbol[1])), "color", "color"),
            "up_is_output": (str(base.DIR_UP in self.outp), "bool",
                             "up is output"),
            "down_is_output": (str(base.DIR_DOWN in self.outp), "bool",
                               "down is output"),
            "left_is_output": (str(base.DIR_LEFT in self.outp), "bool",
                               "left is output"),
            "right_is_output": (str(base.DIR_RIGHT in self.outp), "bool",
                                "right is output"),
            "interval": (str(self.interval), "int", "pulse interval"),
            "offset": (str(self.offset), "int", "pulse offset")
        }
        return props

    def set_exposed_props(self, props):
        props = {key: value[0] for key, value in props.items()}
        color = tuple(int(x) for x in props["color"][1:-1].split(","))
        self.symbol = (props["character"], color, self.symbol[2])

        self.outp = []
        self.outp += [base.DIR_UP] if props["up_is_output"] == "t" else []
        self.outp += [base.DIR_DOWN] if props["down_is_output"] == "t" else []
        self.outp += [base.DIR_LEFT] if props["left_is_output"] == "t" else []
        self.outp += [base.DIR_RIGHT] if props["right_is_output"] == "t" else []

        self.interval = int(props["interval"])
        self.offset = int(props["offset"])

# class Output(Module):
#     symbol = ("u", base.cols["source_fg"], base.cols["bg"])
#     name = "Output"
#     def __init__(self, pos, symbol=None):
#         self.midiout = rtmidi.MidiOut()
#         self.available_ports = self.midiout.get_ports()
#         print(self.available_ports)
#         self.midiout.open_port(1)
#         return super().__init__(pos, symbol)

#     def on_pulse(self, p):
#         note_on = [0x90, 60, 112] # channel 1, middle C, velocity 112
#         note_off = [0x80, 60, 0]
#         self.midiout.send_message(note_on)
#         time.sleep(0.5)
#         self.midiout.send_message(note_off)
#         time.sleep(0.1)
#         return []


#     def get_exposed_props(self):
#         return super().get_exposed_props()

#     def set_exposed_props(self, props):
#         pass


names = ["spreader", "emitter", "empty"]


def name_to_module(name: str, pos: base.Vec2d) -> Module:
    name = name.strip().lower()
    if name == "spreader":
        return Spreader(pos)
    elif name == "emitter":
        return Emitter(pos)
    elif name == "empty":
        return Empty(pos)
    # elif name == "output":
    #     return Output(pos)
    else:
        print("invalid module name", name)
        return None
