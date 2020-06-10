from .Input import Input

class Control(Input):
    def __init__(self, number, type, id):
        super().__init__(number, type, id)
        self.value = 0
        self.control_bank = 1
        self.is_pad = False
        self.is_switch = False
        self.is_transport = False