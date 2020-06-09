# Akai MPD226 Script for FL Studio
Allows the Akai MPD226 to communicate with FL Studio via a Python API.

<img src="https://www.stars-music.com/medias/akai/mpd226-hd-89540.png" alt="MPD226" width="450"/>

1) This project belong in `Image-Line/FL Studio/Settings/Hardware/`
2) In the FL Studio MIDI settings, select `Akai MPD226 (user)` from the controller type dropdown.

### MPD226 button event information
Information on how FL Studio reads the MPD226 buttons.

Note On / Note Off (boolean values)
- Pads 1-16

Control Change (value ranges)
- Knobs 1-4
- Sliders 1-4
- Time Div buttons (1/4, 1/8, 1/16, 1/32)
- Stop button
- Play button
- Rec button

Channel Aftertouch
- Holding a Pad down (action)

No event information
- Full Level button
- 16 Level button
- Tap Tempo button
- Note Repeat button
- Preset button
- Pad Bank button
- Ctrl Bank button
- Edit button
- Global button
- Cursor buttons (Up, Down, Left, Right)
- Menu knob