# name=Akai MPD226

"""
IMPORTANT: On your MPD226, press Edit and change all the Aft: properties of the pads from Chan to Poly.
This allows the pad ids to be passed in with the event data.
Otherwise this script won't recognize Channel Aftertouch targets.
"""

from mpd_data import mpd_device

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