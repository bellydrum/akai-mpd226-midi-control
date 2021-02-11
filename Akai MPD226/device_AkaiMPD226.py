# name=Akai MPD226

"""
HEY! YOU!
 I've made it so you don't have to change anything in this file.
 For all event handling, check next door in MPDHandler.py

IMPORTANT:
 On your MPD226, press Edit and change all the Aft: properties of the pads from Chan to Poly.
 This allows the pad ids to be passed in with the event data.
 Otherwise this script won't recognize Channel Aftertouch targets.
"""

from MPDHandler import MPDHandler

class DeviceInstance(MPDHandler):

    def OnInit(self):
        self.set_port_number()
        self.set_init_time()
        self.last_pad_press_time = self.init_time
        self.last_transport_press_time = self.init_time
        print("Initialized MPD226 on port", self.port, ".")

    def OnMidiMsg(self, event):
        event.handled = False
        self.delegate_event(event)

    def OnDeInit(self):
        pass

    def OnMidiIn(self, event):
        pass

    def OnMidiOutMsg(self, event):
        pass

    def OnIdle(self):
        pass

    def OnRefresh(self, flags):
        pass

    def OnUpdateBeatIndicator(self, value):
        self.handle_beat(value)

    def delegate_event(self, event):
        status = event.status
        try:
            if self.events[status] == "Note On":
                self.delegate_note_on(event)
            elif self.events[status] == "Note Off":
                self.delegate_note_off(event)
            elif self.events[status] == "Control Change":
                self.delegate_control_change(event)
            elif self.events[status] == "Channel Aftertouch (Poly)":
                self.delegate_channel_aftertouch(event)
            elif self.events[status] == "Channel Aftertouch (Channel)":
                print("IMPORTANT: Change pad channel aftertouch settings to poly.")
                event.handled = True
            else:
                print("Event status " + status + " not found in self.events.")
                event.handled = True
        except KeyError:
            print("self.delegate_event error:\n  Event status {status} does not exist.")

    def delegate_note_on(self, event):
        pad = self.get_pad(event.controlNum)
        if pad:
            time_pressed = self.get_timestamp()
            if self.check_buffer(pad, time_pressed):
                self.last_pad_press_time = time_pressed
                pad.on = not pad.on
                pad.held = True
                self.check_for_remap(pad, event)
                self.handle_pad_press(event, pad)
        event.handled = True

    def delegate_note_off(self, event):
        pad = self.get_pad(event.controlNum)
        if pad:
            pad.held = False
            self.handle_pad_release(event, pad)
        event.handled = True

    def delegate_channel_aftertouch(self, event):
        pad = self.get_pad(event.controlNum)
        if pad:
            self.handle_pad_pressure_change(event, pad, event.controlVal)
        else:
            event.handled = True

    def delegate_control_change(self, event):
        id = event.controlNum
        if any([knob.id == id for knob in [self.knob_1, self.knob_2, self.knob_3, self.knob_4]]):
            knob = self.get_knob(id)
            self.handle_knob_change(event, knob, event.controlVal)
        elif any([slider.id == id for slider in [self.slider_1, self.slider_2, self.slider_3, self.slider_4]]):
            slider = self.get_slider(id)
            slider.value = event.controlVal
            if slider.value == self.MODE_CHANGE_UNLOCK_VALUE: self.check_for_mode_change_unlock(slider)
            else:
                if self.mode_change_unlocked:
                    self.set_hint_message("Button remapping mode locked")
                    print("Button remapping mode LOCKED.")
                self.mode_change_unlocked = False
            self.handle_slider_change(event, slider, event.controlVal)
        elif any([switch.id == id for switch in [self.switch_1, self.switch_2, self.switch_3, self.switch_4]]):
            switch = self.get_switch(id)
            switch.on = not switch.on
            self.handle_switch_press(event, switch)
        elif any([transport.id == id for transport in [self.stop, self.play, self.rec]]):
            self.delegate_transport_press(event, self.get_transport(id))
        else:
            print("Input not found for event.controlNum " + str(id) + ".")
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


mpd_device = DeviceInstance()

def OnInit():
    mpd_device.OnInit()

def OnDeInit():
    pass

def OnMidiIn(event):
    pass

def OnMidiOutMsg(event):
    pass

def OnMidiMsg(event):
    mpd_device.OnMidiMsg(event)

def OnIdle():
    pass

def OnRefresh(flags):
    pass

def OnUpdateBeatIndicator(value):
    mpd_device.OnUpdateBeatIndicator(value)
