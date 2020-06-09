import time

import arrangement
import channels
import mixer
import general
import patterns
import playlist
import screen
import transport
import ui

import device
import launchMapPages
import midi
import utils

from classes.MPD226 import MPD226

class CurrentDevice(MPD226):

    init_time = time.perf_counter()
    last_pad_press_time = init_time
    last_stop_press_time = init_time

    def OnInit(self):
        mpd_device.port = device.getPortNumber()
        print(f"Initialized MPD226 on port {mpd_device.port}.")

    def OnMidiMsg(self, event):
        self.delegate_event(event)

    def check_buffer(self, button, time_pressed):
        if button.type == 'transport':
            return time_pressed - self.last_stop_press_time > self.STOP_BUFFER
        elif button.type == 'pad':
            return time_pressed - self.last_pad_press_time > self.PAD_BUFFER
        else:
            print(f"{button.type.upper()} {button.number} has no associated buffer.")

    def delegate_event(self, event):
        status = event.status
        if self.events[status] == "Note On":
            self.delegate_note_on(event)
        elif self.events[status] == "Note Off":
            self.delegate_note_off(event)
        elif self.events[status] == "Control Change":
            self.delegate_control_change(event)
        elif self.events[status] == "Channel Aftertouch (Poly)":
            self.delegate_channel_aftertouch(event)
        elif self.events[status] == "Channel Aftertouch (Channel)":
            print("ERROR: Change pad channel aftertouch settings to poly.")
            event.handled = True
        else:
            print(f"Event status {status} not found in self.events.")
            event.handled = True

    def delegate_note_on(self, event):
        pad = self.get_pad(event.controlNum)
        time_pressed = time.perf_counter()
        if self.check_buffer(pad, time_pressed):
            self.last_pad_press_time = time_pressed
            pad.on = not pad.on
            self.handle_pad_press(event, pad)
        else:
            event.handled = True

    def delegate_note_off(self, event):
        self.handle_pad_release(event, self.get_pad(event.controlNum))

    def delegate_channel_aftertouch(self, event):
        pad = self.get_pad(event.controlNum)
        self.handle_pad_pressure_change(event, pad, event.controlVal)

    def delegate_control_change(self, event):
        id = event.controlNum
        if any([knob.id == id for knob in [self.knob_1, self.knob_2, self.knob_3, self.knob_4]]):
            knob = self.get_knob(id)
            self.handle_knob_change(event, knob, event.controlVal)
        elif any([slider.id == id for slider in [self.slider_1, self.slider_2, self.slider_3, self.slider_4]]):
            slider = self.get_slider(id)
            self.handle_slider_change(event, slider, event.controlVal)
        elif any([switch.id == id for switch in [self.switch_1, self.switch_2, self.switch_3, self.switch_4]]):
            switch = self.get_switch(id)
            switch.on = not switch.on
            self.handle_switch_press(event, switch)
        elif any([transport.id == id for transport in [self.stop, self.play, self.rec]]):
            self.delegate_transport_press(event, self.get_transport(id))
        else:
            print(f"Input not found for event.controlNum {id}.")
            event.handled = True

    def delegate_transport_press(self, event, transport):
        if transport.number == 1:
            self.stop.on = not self.stop.on
            self.handle_stop_press(event, transport)
        elif transport.number == 2:
            self.play.on = not self.play.on
            self.handle_play_press(event, transport)
        elif transport.number == 3:
            self.rec.on = not self.rec.on
            self.handle_rec_press(event, transport)
        else:
            event.handled = True

    def handle_pad_press(self, event, pad):
        """
        Put pad press code here.
        """
        print(f"Pressed pad {pad.number}.")

        event.handled = True

    def handle_pad_release(self, event, pad):
        """
        Put pad release code here.
        """
        print(f"Released pad {pad.number}.")

        event.handled = True

    def handle_pad_pressure_change(self, event, pad, value):
        """
        Put pad pressure change code here.
        """
        print(f"Changed pad {pad.number} pressure to {value}.")

        event.handled = True

    def handle_knob_change(self, event, knob, value):
        """
        Put knob change code here.
        """
        print(f"Changed knob {knob.number} to {value}.")

        event.handled = True

    def handle_slider_change(self, event, slider, value):
        """
        Put slider change code here.
        """
        print(f"Changed slider {slider.number} to {value}.")

        event.handled = True

    def handle_switch_press(self, event, switch):
        """
        Put switch press code here.
        """
        print(f"Pressed switch {switch.number}.")

        event.handled = True

    def handle_stop_press(self, event, stop):
        """
        Put stop press code here.
        """
        print(f"Pressed stop button.")

        event.handled = True

    def handle_play_press(self, event, play):
        """
        Put play press code here.
        """
        print(f"Pressed play button.")

        event.handled = True

    def handle_rec_press(self, event, rec):
        """
        Put rec press code here.
        """
        print(f"Pressed rec button.")

        event.handled = True

mpd_device = CurrentDevice()