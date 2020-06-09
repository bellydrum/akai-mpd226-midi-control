from .Input import Input

class Button(Input):
    def __init__(self, number, type, id):
        super().__init__(number, type, id)
        self.note = None
        self.held = False
        self.on = False
        self.is_knob = False
        self.is_slider = False