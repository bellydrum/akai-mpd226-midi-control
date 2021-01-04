# name=Akai MPD226 BACKUP

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


# TODO BUG FIX - knob / slider values go up to 127, which is 27 higher than what FL understands
#   - EXAMPLE: in mixer.setTrackVolume(1, 1.27), the 1.27 will be read as 1)
#   - POSSIBLE FIX - adjust self.setTargetValue() units so that [1-127] maps to [1-100]
# TODO: BUG FIX - pad pressure changes only affect last pad pressed (aka current self.TARGET)
#   - this is because Channel Aftertouch events don't come with an input id
#   - POSSIBLE FIX - find input id in Channel Aftertouch events

# event names
#   153     Note On
#   137     Note Off
#   176     Control Change
#   217     Channel Aftertouch
#   ???     Key Aftertouch
#   ???     Program Change
#   ???     Pitch Bend
#   ???     System Message

""" GLOBAL INPUT ID CONSTANTS"""
PAD_IDS = [ 37, 36, 42, 82, 40, 38, 46, 44, 48, 47, 45, 43, 49, 55, 51, 53 ]
KNOB_IDS = [ 3, 9, 14, 15 ]
SLIDER_IDS = [ 20, 21, 22, 23 ]
TIME_DIV_BUTTON_IDS = [ 28, 29, 30, 31 ]
TRANSPORT_BUTTON_IDS = [ 117, 118, 119 ]
""" GLOBAL INPUT NAME CONSTANTS """
TIME_DIV_VALS = [ '1/4', '1/8', '1/16', '1/32' ]
TRANSPORT_BUTTON_VALS = [ 'Stop', 'Play', 'Rec' ]
INPUT_TYPES = [ 'pad', 'knob', 'slider', 'time div button', 'transport button' ]
""" GLOBAL SYSTEM CONSTANTS """
PAD_BUFFER = 0.10
NUMBER_OF_WINDOW_TYPES = 4
INPUT_MODES = [ 'default', 'ui', 'transport' ]

class Input:
    """ Represents an input on the MPD226 device. """
    def __init__(self, id, name, type, pressed, toggle):
        self.id = id
        self.name = name
        self.type = type
        self.pressed = pressed
        self.toggle = toggle


class MPD226:
    """ Represents the MPD226 device."""

    """
    Internal constants
    """

    """ Constants that are manipulated by getters and setters """
    INPUT_MODE = INPUT_MODES[0]
    MODE_CHANGE_UNLOCKED = False
    TARGET = None
    TARGET_TYPE = None
    TARGET_VALUE = 0
    TARGET_PRESSURE = 0
    LAST_PAD_PRESSED = None
    LAST_PAD_PRESSED_TIMESTAMP = time.perf_counter()
    CURRENT_FOCUSED_WINDOW = 0
    HINT_MESSAGE = None

    """ Custom Input objects that represent all the inputs on the MPD226 and their current states """
    PADS_BY_NUMBER = [
        Input(PAD_IDS[pad_id], f'Pad {pad_id + 1}', INPUT_TYPES[0], False, False)
        for pad_id in range(len(PAD_IDS))
    ]
    PADS_BY_ID = {i.id: i for i in PADS_BY_NUMBER}
    KNOBS_BY_NUMBER = [
        Input(KNOB_IDS[knob_id], f'Knob {knob_id + 1}', INPUT_TYPES[1], False, False)
        for knob_id in range(len(KNOB_IDS))
    ]
    KNOBS_BY_ID = {i.id: i for i in KNOBS_BY_NUMBER}
    SLIDERS_BY_NUMBER = [
        Input(SLIDER_IDS[slider_id], f'Slider {slider_id + 1}', INPUT_TYPES[2], False, False)
        for slider_id in range(len(SLIDER_IDS))
    ]
    SLIDERS_BY_ID = {i.id: i for i in SLIDERS_BY_NUMBER}
    TIME_DIV_BUTTONS_BY_NUMBER = [
        Input(TIME_DIV_BUTTON_IDS[tdb_id], f'{TIME_DIV_VALS[tdb_id]}', INPUT_TYPES[3], False, False)
        for tdb_id in range(len(TIME_DIV_BUTTON_IDS))
    ]
    TIME_DIV_BUTTONS_BY_ID = {i.id: i for i in TIME_DIV_BUTTONS_BY_NUMBER}
    TRANSPORT_BUTTONS_BY_NUMBER = [
        Input(TRANSPORT_BUTTON_IDS[tb_id], f'{TRANSPORT_BUTTON_VALS[tb_id]}', INPUT_TYPES[4], False, False)
        for tb_id in range(len(TRANSPORT_BUTTON_IDS))
    ]
    TRANSPORT_BUTTONS_BY_ID = {i.id: i for i in TRANSPORT_BUTTONS_BY_NUMBER}

    def __init__(self):
        return

    """
    Getters and setters
    """

    def setHintMessage(self, message):
        if isinstance(message, str): ui.setHintMsg(message)
        else: print("self.setHintMessage error:\n  Param 'message' must be of type str.")

    """ Get and set input mode information """
    def getInputMode(self):
        return self.INPUT_MODE

    def setInputMode(self, target, mode='increment'):
        if isinstance(target, Input):
            if isinstance(mode, str):
                if mode in INPUT_MODES:
                    self.INPUT_MODE = mode
                elif mode == 'increment':
                    if target == self.getPadByNumber(4):
                        self.INPUT_MODE = INPUT_MODES[(INPUT_MODES.index(self.getInputMode()) + 1) % len(INPUT_MODES)]
                    elif target == self.getPadByNumber(1):
                        self.INPUT_MODE = INPUT_MODES[(INPUT_MODES.index(self.getInputMode()) - 1) % len(INPUT_MODES)]
                    self.setHintMessage(f"{self.INPUT_MODE} mode".upper())
                print("\nInput mode changed to " + self.INPUT_MODE + ".\n")
            else: print("self.setInputMode error:\n  Param 'mode' " + mode + " must be of type str.")
        else: print("self.setInputMode error:\n  Param 'target' " + target + " must be of type Input.")

    def cycleWindowFocus(self, value):
        self.CURRENT_FOCUSED_WINDOW = (self.CURRENT_FOCUSED_WINDOW + value) % (NUMBER_OF_WINDOW_TYPES + 1)
        ui.showWindow(self.CURRENT_FOCUSED_WINDOW)

    """ Get pad Input objects """
    def getPadById(self, id):
        if isinstance(id, int):
            return self.PADS_BY_ID[id] if id in PAD_IDS else None
        else: print("self.getPadById error:\n  Param 'id' " + str(id) + " must be of type int.")

    def getPadByNumber(self, number):
        if isinstance(number, int):
            return self.PADS_BY_NUMBER[number - 1] if number in range(1, len(PAD_IDS) + 1) \
                else print("self.getPadByNumber error:\n  Param 'number' " + str(number) + " must be in range.")
        else: print("self.getPadByNumber error:\n  Param 'number' " + str(number) + " must be of type int.")

    """ Get knob Input objects """
    def getKnobById(self, id):
        if isinstance(id, int):
            return self.KNOBS_BY_ID[id] if id in KNOB_IDS else None
        else: print("self.getKnobById error:\n  Param 'id' " + str(id) + " must be of type int.")

    def getKnobByNumber(self, number):
        if isinstance(number, int):
            return self.KNOBS_BY_NUMBER[number - 1] if number in range(1, len(KNOB_IDS) + 1) \
                else print("self.getKnobByNumber error:\n  Param 'number' " + str(number) + " must be in range.")
        else: print("self.getKnobByNumber error:\n  Param 'number' " + str(number) + " must be of type int.")

    """ Get slider Input objects """
    def getSliderById(self, id):
        if isinstance(id, int):
            return self.SLIDERS_BY_ID[id] if id in SLIDER_IDS else None
        else: print("self.getSliderById error:\n  Param 'id' " + str(id) + " must be of type int.")

    def getSliderByNumber(self, number):
        if isinstance(number, int):
            return self.SLIDERS_BY_NUMBER[number - 1] if number in range(1, len(SLIDER_IDS) + 1) \
                else print("self.getSliderByNumber error:\n  Param 'number' " + str(number) + " must be in range.")
        else: print("self.getSliderByNumber error:\n  Param 'number' " + str(number) + " must be of type int.")

    """ Get time division Input objects """
    def getTimeDivButtonById(self, id):
        if isinstance(id, int):
            return self.TIME_DIV_BUTTONS_BY_ID[id] if id in TIME_DIV_BUTTON_IDS else None
        else: print("self.getTimeDivButtonById error:\n  Param 'id' " + str(id) + " must be of type int.")

    def getTimeDivButtonByNumber(self, number):
        if isinstance(number, int):
            return self.TIME_DIV_BUTTONS_BY_NUMBER[number - 1] if number in range(1, len(TIME_DIV_BUTTON_IDS) + 1) \
                else print("self.getTimeDivButtonByNumber error:\n  Param 'number' " + str(number) + " must be in range.")
        else: print("self.getTimeDivButtonByNumber error:\n  Param 'number' " + str(number) + " must be of type int.")

    """ Get transport button input objects """
    def getTransportButtonById(self, id):
        if isinstance(id, int):
            return self.TRANSPORT_BUTTONS_BY_ID[id] if id in TRANSPORT_BUTTON_IDS else None
        else: print("self.getTransportButtonById error:\n  Param 'id' " + str(id) + " must be of type int.")

    def getTransportButtonByNumber(self, number):
        if isinstance(number, int):
            return self.TRANSPORT_BUTTONS_BY_NUMBER[number - 1] if number in range(1, len(TRANSPORT_BUTTON_IDS) + 1) \
                else print("self.getTransportButtonByNumber error:\n  Param 'number' " + str(number) + " must be in range.")
        else: print("self.getTransportButtonByNumber error:\n  Param 'number' " + str(number) + " must be of type int.")

    """ Get and set current target input """
    def getTarget(self):
        return self.TARGET

    def setTarget(self, target):
        self.TARGET, self.TARGET_TYPE = target, target.type if isinstance(target, Input) \
            else print("self.setTarget error:\n  Target " + str(target) + " must be of type Input.")

    def getTargetType(self):
        return self.TARGET_TYPE

    def setTargetType(self, type=None):
        self.TARGET_TYPE = type if type in INPUT_TYPES \
            else print("self.setTargetType error:\n  Param 'type' " + str(type) + " must exist in TARGET_TYPES.")

    def getTargetValue(self):
        return self.TARGET_VALUE / 100 if self.TARGET_VALUE < 100 else 1

    def setTargetValue(self, value=0):
        if isinstance(value, int): self.TARGET_VALUE = value if value < 101 else 100
        else: print("self.setTargetValue error:\n  Param 'value' " + str(value) + " must be of type int.")

    def getTargetPressure(self):
        return self.TARGET_PRESSURE

    def setTargetPressure(self, pressure=0):
        if isinstance(pressure, int): self.TARGET_PRESSURE = pressure if pressure < 128 else 127
        else: print("self.setTargetPressure error:\n  Param 'pressure' " + str(pressure) + " must be of type int.")

    def getLastPadPressed(self):
        return self.LAST_PAD_PRESSED

    def setLastPadPressed(self, pad_target):
        if isinstance(pad_target, Input):
            if pad_target.type == INPUT_TYPES[0]:
                self.LAST_PAD_PRESSED = pad_target
            else:
                print("self.setLastPadPressed error:\n  Param 'pad_target' type " + str(pad_target.type) + " must be 'pad'.")
        else:
            print("self.setLastPadPressed error:\n  Param 'pad_target' " + str(pad_target) + " must be of type Input.")

    """ Get type of current target input """
    def targetIsPad(self):
        return self.TARGET_TYPE == INPUT_TYPES[0]

    def targetIsKnob(self):
        return self.TARGET_TYPE == INPUT_TYPES[1]

    def targetIsSlider(self):
        return self.TARGET_TYPE == INPUT_TYPES[2]

    def targetIsTimeDivButton(self):
        return self.TARGET_TYPE == INPUT_TYPES[3]

    def targetIsTransportButton(self):
        return self.TARGET_TYPE == INPUT_TYPES[4]

    """ Update pad pressed state """
    def updatePadPressedStateById(self, id, status):
        if isinstance(status, bool):
            self.PADS_BY_ID[id].pressed = status if id in PAD_IDS \
                else print(f"self.updatePressedStateById error:\n  Param 'id' must exist in PAD_IDS.")
        else: print(f"self.updatePressedStateById error:\n  Param 'status' {status} must be of type bool.")

    def updatePadPressedStateByNumber(self, number, status):
        self.PADS_BY_NUMBER[number].pressed = status if isinstance(status, bool) \
            else print(f"self.updatePressedStateByNumber error:\n  Param 'status' {status} musy be of type bool.")

    """ Update pad toggle state """
    def updatePadToggleStateById(self, id):
        if isinstance(id, int):
            self.PADS_BY_ID[id].toggle = not self.PADS_BY_ID[id].toggle if id in PAD_IDS \
                else print(f"self.updatePadToggleStateById error:\n  Param 'id' {id} must exist in PAD_IDS.")
        else: print(f"self.updatePadToggleStateById error:\n  Param 'id' {id} must be of type int.")

    def updatePadToggleStateByNumber(self, number):
        if isinstance(id, int):
            self.PADS_BY_NUMBER[number].toggle = not self.PADS_BY_ID[id].toggle \
                if number in range(1, len(PAD_IDS) + 1) \
                else print(f"self.updatePadToggleStateByNumber error:\n  Param 'number' {number} must be in range.")
        else: print(f"self.updatePadToggleStateByNumber error:\n  Param 'number' {number} musy be of type int.")

    def updateKnobOrSliderToggleState(self, target, value):
        if isinstance(target, Input):
            if isinstance(value, bool): target.toggle = value
            else: print(f"self.updateKnobSliderToggleStateById error:\n  Param 'value' {id} must be of type bool.")
        else: print(f"self.updateKnobSliderToggleStateById error:\n  Param 'target' {id} must be of type Input.")

    def updateTimeDivToggleStateById(self, id):
        if isinstance(id, int):
            self.TIME_DIV_BUTTONS_BY_ID[id].toggle = not self.TIME_DIV_BUTTONS_BY_ID[id].toggle \
                if id in TIME_DIV_BUTTON_IDS \
                else print(f"self.updateTimeDivToggleStateById error:\n"
                    f"  Param 'id' {id} must exist in TIME_DIV_BUTTON_IDS.")
        else: print(f"self.updateTimeDivToggleStateById error:\n  Param 'id' {id} must be of type int.")

    def updateTimeDivToggleStateByNumber(self, number):
        if isinstance(id, int):
            self.TIME_DIV_BUTTONS_BY_NUMBER[number].toggle = not self.TIME_DIV_BUTTONS_BY_NUMBER[id].toggle \
                if number in range(1, len(TIME_DIV_BUTTON_IDS) + 1) \
                else print(f"self.updateTimeDivToggleStateByNumber error:\n  Param 'number' {number} must be in range.")
        else: print(f"self.updateTimeDivToggleStateByNumber error:\n  Param 'number' {number} musy be of type int.")

    """
    Input mode control
    """
    def checkForModeChange(self, target, pad_input_timestamp):
        """ Check to see if current input(s) should change the input mode for FL Studio. """

        # hold pads 13 and 16 to be able to change modes with pads 1 and 4
        mode_change_lock_inputs = [ self.getPadByNumber(i) for i in [ 13, 16 ] ]
        mode_change_nav_inputs = [ self.getPadByNumber(i) for i in [ 1, 4 ] ]
        if target in mode_change_nav_inputs and all(pad.pressed for pad in mode_change_lock_inputs):
            self.setInputMode(target)
            if (pad_input_timestamp - self.LAST_PAD_PRESSED_TIMESTAMP) < PAD_BUFFER: return None
            self.LAST_PAD_PRESSED_TIMESTAMP = pad_input_timestamp

    """
    Event listeners
    """
    def onInit(self):
        print("\nAkai MPD226 script loaded.")
        print("Make sure your MPD226 is set to the FlStudio preset.")
        print("If inputs are still being read incorrectly, you can:\n  Make sure the input id constants are correct.")
        print("  You can do this by checking the debugging log and updating the input id constants accordingly.\n")

    def onDeInit(self):
        print('deinit ready')

    def determineValueInputType(self, event):
        # print(f"self.determineValueInputType called for {event.status} {event.data1} {event.data2}")

        # determine what type of input is changing its value
        knob_target = self.getKnobById(event.data1)
        slider_target = self.getSliderById(event.data1)
        time_div_target = self.getTimeDivButtonById(event.data1)
        transport_target = self.getTransportButtonById(event.data1)

        if knob_target:
            self.setTarget(knob_target)
            self.setTargetValue(event.data2)
            self.handleKnobChange(knob_target, event.data2)
        elif slider_target:
            self.setTarget(slider_target)
            self.setTargetValue(event.data2)
            self.handleSliderChange(slider_target, event.data2)
        elif time_div_target:
            self.setTarget(time_div_target)
            self.setTargetValue(event.data2)
            self.handleTimeDivisionButtonPress(time_div_target)
        elif transport_target:
            self.setTarget(transport_target)
            self.setTargetValue(event.data2)
            self.handleTransportButtonChange(transport_target, event.data2)
        else:
            print(f"self.determineValueInputType error:\n  Param 'event' {event} value 'data1' {event.data1} not found.")

    """
    Event handlers
    """
    def handlePadPress(self, event):
        # print(f"self.handlePadPress called for {event.status} {event.data1} {event.data2}")

        """ Cancel pad input if it happens too soon after the last pad input """
        pad_input_timestamp = time.perf_counter()
        current_input_mode = self.getInputMode()

        target = self.getPadById(event.data1)
        value = True
        if target:
            self.setTarget(target)
            self.updatePadPressedStateById(target.id, value)
            self.updatePadToggleStateById(target.id)
            self.setLastPadPressed(target)
            if self.MODE_CHANGE_UNLOCKED:
                self.checkForModeChange(target, pad_input_timestamp)
        else:
            print(f"self.handlePadPress error:\n  Pad not found for {event.data1}.")
            return None
        if current_input_mode != self.getInputMode():
            event.handled = True
            return None
        print(f"{target.name} pressed")

        """
        Start custom events here.
        """

        if self.getInputMode() == 'ui':

            if target == self.getPadByNumber(16):
                self.cycleWindowFocus(1)
            elif target == self.getPadByNumber(15):
                self.cycleWindowFocus(-1)
            elif target == self.getPadByNumber(12):
                ui.next()
                self.LAST_PAD_PRESSED_TIMESTAMP = time.perf_counter()
            elif target == self.getPadByNumber(11):
                ui.previous()
                self.LAST_PAD_PRESSED_TIMESTAMP = time.perf_counter()

        """
        End custom events here.
        """
        # TODO - set event to handled

    def handlePadRelease(self, event):
        # print(f"self.handlePadRelease called for {event.status} {event.data1} {event.data2}")

        target = self.getPadById(event.data1)
        value = False
        if target:
            self.setTarget(target)
            self.updatePadPressedStateById(target.id, value)
            self.LAST_PAD_PRESSED_TIMESTAMP = time.perf_counter()
        else:
            print(f"self.handlePadRelease error:\n  Pad not found for {event.data1}.")
            return None
        print(f"{target.name} released")

        """
        Start custom events here.
        """

        """
        End custom events here.
        """
        # TODO - set event to handled

    def handlePressureChange(self, event):
        # print(f"self.handlePressureChange called for {event.status} {event.data1} {event.data2}")

        # BUG WARNING - pressure assignment only happens to the most recent pad pressed (see notes at top of file)
        #   - until fixed, the assumption is that self.getTarget() would return the pad whose pressure is changing.
        self.setTarget(self.getLastPadPressed())
        self.setTargetPressure(event.data1)
        target = self.getTarget()
        value = event.data1
        print(f"{target.name} pressure changed to {value}")

        """
        Start custom events here.
        """

        if self.getInputMode() == 'ui':
            if self.LAST_PAD_PRESSED == self.getPadByNumber(12):
                if (time.perf_counter() - self.LAST_PAD_PRESSED_TIMESTAMP) > (PAD_BUFFER * 2.5):
                    ui.next()
            elif self.LAST_PAD_PRESSED == self.getPadByNumber(11):
                if (time.perf_counter() - self.LAST_PAD_PRESSED_TIMESTAMP) > (PAD_BUFFER * 2.5):
                    ui.previous()

        """
        End custom events here.
        """
        # TODO - set event to handled

    def handleKnobChange(self, target, value):
        # print(f"self.handlePressureChange called for {event.status} {event.data1} {event.data2}")
        print(f"{target.name} changed to {value}")

        """
        Start custom events here.
        """

        """
        End custom events here.
        """
        # TODO - set event to handled

    def handleSliderChange(self, target, value):
        # print(f"self.handlePressureChange called for {event.status} {event.data1} {event.data2}")
        print(f"{target.name} changed to {value}")

        # handle input mode change lock
        if self.getInputMode() == 'ui':
            # if mixer:
            if target == self.getSliderByNumber(1):
                print(f"Changing volume to {self.getTargetValue()} on track {mixer.trackNumber()}")
                mixer.setTrackVolume(mixer.trackNumber(), self.getTargetValue() if self.getTargetValue() < .8 else .8)
        else:
            self.updateKnobOrSliderToggleState(target, value != 127)

        self.MODE_CHANGE_UNLOCKED = all(slider.toggle == False for slider in [ self.getSliderByNumber(i) for i in range(1, 5)])

        """
        Start custom events here.
        """

        """
        End custom events here.
        """
        # TODO - set event to handled

    def handleTimeDivisionButtonPress(self, target):
        # print(f"self.handlePressureChange called for {event.status} {event.data1} {event.data2}")
        print(f"{target.name} toggled to {'On' if target.toggle else 'Off'}")

        self.updateTimeDivToggleStateById(target.id)

        """
        Start custom events here.
        """

        """
        End custom events here.
        """
        # TODO - set event to handled

    def handleTransportButtonChange(self, target, value):
        # print(f"self.handlePressureChange called for {event.status} {event.data1} {event.data2}")
        print(f"{target.name} changed to {value}")

        """
        Start custom events here.
        """

        """
        End custom events here.
        """
        # TODO - set event to handled


mpd_device = MPD226()

def OnInit():
    mpd_device.onInit()

def OnDeInit():
    mpd_device.onDeInit()

def OnMidiMsg(event):
    """ Handles general midi events. """

    """ Initialize states """
    print("\n-----------------------------\n")

    mpd_device.TARGET = None
    mpd_device.TARGET_TYPE = None
    mpd_device.TARGET_VALUE = 0
    mpd_device.TARGET_PRESSURE = 0

    print(f'event.handled: {event.handled}')
    print(f'event.timestamp: {event.timestamp}')
    print(f'event.port: {event.port}')
    print(f'event.midiId: {event.midiId}')
    print(f'event.midiChan: {event.midiChan}')

    print('\n')
    print(f'event.status: {event.status}')
    print(f'event.data1: {event.data1}')
    print(f'event.data2: {event.data2}')

    print('\n')
    print(f'event.note: {event.note}')
    print(f'event.velocity: {event.velocity}')
    print(f'event.pressure: {event.pressure}')

    print('\n')
    print(f'event.progNum: {event.progNum}')
    print(f'event.controlNum: {event.controlNum}')
    print(f'event.controlVal: {event.controlVal}')

    print('\n')
    print(f'event.isIncrement: {event.isIncrement}')

    print("\n-----------------------------\n")




    # """ Determine event type """
    # pressed = event.status == 153
    # released = event.status == 137
    # pressure_changed = event.status == 217
    # value_changed = event.status == 176
    #
    # """ Send event to appropriate event type handler """
    # if pressed: mpd_device.handlePadPress(event)
    # elif released: mpd_device.handlePadRelease(event)
    # elif pressure_changed: mpd_device.handlePressureChange(event)
    # elif value_changed: mpd_device.determineValueInputType(event)
    # else: print(f"OnMidiMsg error:\n  Event not found for {event.status}.\n")

    # mpd_device.onMidiMsg(event)