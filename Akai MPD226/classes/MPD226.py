from .MPD226Input import *

class MPD226:

    pad_1 = Pad(1, 'pad', 37)  # C#2
    pad_2 = Pad(2, 'pad', 36)  # C2
    pad_3 = Pad(3, 'pad', 42)  # F#2
    pad_4 = Pad(4, 'pad', 82)  # A#5
    pad_5 = Pad(5, 'pad', 40)  # E2
    pad_6 = Pad(6, 'pad', 38)  # D2
    pad_7 = Pad(7, 'pad', 46)  # A#2
    pad_8 = Pad(8, 'pad', 44)  # G#2
    pad_9 = Pad(9, 'pad', 48)  # C3
    pad_10 = Pad(10, 'pad', 47)  # B2
    pad_11 = Pad(11, 'pad', 45)  # A2
    pad_12 = Pad(12, 'pad', 43)  # G2
    pad_13 = Pad(13, 'pad', 49)  # C#3
    pad_14 = Pad(14, 'pad', 55)  # G3
    pad_15 = Pad(15, 'pad', 51)  # D#3
    pad_16 = Pad(16, 'pad', 53)  # F3
    knob_1 = Knob(1, 'knob', 3)
    knob_2 = Knob(2, 'knob', 9)
    knob_3 = Knob(3, 'knob', 14)
    knob_4 = Knob(4, 'knob', 15)
    slider_1 = Slider(1, 'slider', 20)
    slider_2 = Slider(2, 'slider', 21)
    slider_3 = Slider(3, 'slider', 22)
    slider_4 = Slider(4, 'slider', 23)
    switch_1 = Switch(1, 'switch', 28)
    switch_2 = Switch(2, 'switch', 29)
    switch_3 = Switch(3, 'switch', 30)
    switch_4 = Switch(4, 'switch', 31)
    stop = Transport(1, 'transport', 117)
    play = Transport(2, 'transport', 118)
    rec = Transport(3, 'transport', 119)

    PAD_BUFFER = 0.1
    STOP_BUFFER = 2

    INPUT_MODES = ['default', 'ui', 'transport']
    MODE_CHANGE_UNLOCK_VALUE = 127

    def __init__(self):
        self.events = {
            153: 'Note On',
            144: 'Note On',  # custom preset value
            137: 'Note Off',
            128: 'Note Off',  # custom preset value
            176: 'Control Change',
            185: 'Control Change',  # custom preset value
            169: 'Channel Aftertouch (Poly)',
            160: 'Channel Aftertouch (Poly)',  # custom preset value
            217: 'Channel Aftertouch (Channel)',
            208: 'Channel Aftertouch (Channel)'  # custom preset value
        }
        self.pads_by_id = {
            37: self.pad_1,
            36: self.pad_2,
            42: self.pad_3,
            82: self.pad_4,
            40: self.pad_5,
            38: self.pad_6,
            46: self.pad_7,
            44: self.pad_8,
            48: self.pad_9,
            47: self.pad_10,
            45: self.pad_11,
            43: self.pad_12,
            49: self.pad_13,
            55: self.pad_14,
            51: self.pad_15,
            53: self.pad_16
        }
        self.knobs_by_id = {
            3: self.knob_1,
            9: self.knob_2,
            14: self.knob_3,
            15: self.knob_4
        }
        self.sliders_by_id = {
            20: self.slider_1,
            21: self.slider_2,
            22: self.slider_3,
            23: self.slider_4
        }
        self.switches_by_id = {
            28: self.switch_1,
            29: self.switch_2,
            30: self.switch_3,
            31: self.switch_4
        }
        self.transports_by_id = {
            117: self.stop,
            118: self.play,
            119: self.rec
        }

    def get_pad(self, pad_id):
        try:
            return self.pads_by_id[pad_id]
        except KeyError:
            print("self.get_pad error:\n  No pad with id " + str(pad_id) + ".")

    def get_knob(self, knob_id):
        try:
            return self.knobs_by_id[knob_id]
        except KeyError:
            print("self.get_knob error:\n  No knob with id " + str(knob_id) + ".")

    def get_slider(self, slider_id):
        try:
            return self.sliders_by_id[slider_id]
        except KeyError:
            print("self.get_slider error:\n  No slider with id " + str(slider_id) + ".")

    def get_switch(self, switch_id):
        try:
            return self.switches_by_id[switch_id]
        except:
            print("self.get_switch error:\n  No switch with id " + str(switch_id) + ".")

    def get_transport(self, transport_id):
        try:
            return self.transports_by_id[transport_id]
        except:
            print("self.get_transport error:\n  No transport with id " + str(transport_id) + ".")
