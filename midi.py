import time
import rtmidi
from threading import Thread


class Midi():
    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.available_ports = self.midiout.get_ports()
        print(self.available_ports)
        if not self.available_ports:
            print ("No midi server found! Functionality disabled.")

        self.midiout.open_port(0)   #TODO: choose


    def note_thread(self, note, channel, duration):
        note_on = [0x90 + channel, note, 112] # channel 1, middle C, velocity 112
        note_off = [0x80 + channel, note, 0]
        self.midiout.send_message(note_on)
        time.sleep(duration)
        self.midiout.send_message(note_off)

    def play_note(self, note, channel = 0, duration = 0.2):
        t = Thread(target=self.note_thread, args=(note, channel, duration))
        t.start()

midi = Midi()
