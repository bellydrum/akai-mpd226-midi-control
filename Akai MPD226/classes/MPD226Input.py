from .Button import Button
from .Control import Control

class Pad(Button):
    def __init__(self, number, type, id):
        Button.__init__(self, number, type, id)
        self.pad_bank = 1
        self.is_pad = True
        self.is_switch = False
        self.is_transport = False

class Knob(Control):
    def __init__(self, number, type, id):
        Control.__init__(self, number, type, id)
        self.is_knob = True
        self.is_slider = False

class Slider(Control):
    def __init__(self, number, type, id):
        Control.__init__(self, number, type, id)
        self.is_slider = True
        self.is_knob = False

class Switch(Button):
    def __init__(self, number, type, id):
        Button.__init__(self, number, type, id)
        self.is_switch = True
        self.is_pad = False
        self.is_transport = False

class Transport(Button):
    def __init__(self, number, type, id):
        Button.__init__(self, number, type, id)
        self.is_transport = True
        self.is_pad = False
        self.is_switch = False