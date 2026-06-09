# QWERTY MIDI Keyboard

Turn your **computer typing keyboard** into a fully functional MIDI piano controller. Connect it to **Pianoteq**, any DAW, or any VST that accepts MIDI input via a virtual MIDI port.

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)

## How It Works

```
┌──────────────────┐      ┌───────────────┐      ┌──────────────┐
│  Your Keyboard   │ ───► │  This App     │ ───► │  loopMIDI    │ ───► Pianoteq / DAW
│  (QWERTY keys)   │      │  (sends MIDI) │      │  (virtual    │
└──────────────────┘      └───────────────┘      │   MIDI port) │
                                                  └──────────────┘
```

## Setup (Windows)

### 1. Install loopMIDI (one-time)

Download and install [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) — a free virtual MIDI port driver for Windows.

1. Run loopMIDI
2. Type a port name (e.g., `"QWERTY Piano"`) and click **+** to create it
3. Leave loopMIDI running in the system tray

### 2. Install this app

```bash
# Clone the repo
git clone https://github.com/CppDevVS2026/qwerty-midi-keyboard.git
cd qwerty-midi-keyboard

# Install dependencies (use a venv if you prefer)
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### 3. Run

```bash
python -m qwerty_midi.main
# or if installed as package:
qwerty-midi
```

### 4. Connect to Pianoteq

1. In the app, select your loopMIDI port from the dropdown and click **Connect**
2. In Pianoteq → Options → MIDI → set MIDI Input to the same loopMIDI port
3. Start playing!

## Keyboard Layout

The keyboard uses a standard two-row piano layout (same as most DAWs):

### Lower Octave (starting at base note)
```
 Black keys:  S  D     G  H  J     L  ;
              │  │     │  │  │     │  │
 White keys: Z  X  C  V  B  N  M  ,  .  /
             C  D  E  F  G  A  B  C  D  E
```

### Upper Octave (+12 semitones)
```
 Black keys:  2  3     5  6  7     9  0  =
              │  │     │  │  │     │  │  │
 White keys: Q  W  E  R  T  Y  U  I  O  P  [  ]
             C  D  E  F  G  A  B  C  D  E  F  G
```

### Controls
| Key | Action |
|-----|--------|
| `←` / `→` | Shift octave down / up |
| `Space` | Sustain pedal (hold) |
| Velocity slider | Adjust note velocity (1–127) |

## Features

- **Real-time MIDI output** — zero-latency key-to-note conversion
- **Visual piano display** — see which notes are active with color highlights
- **Octave shifting** — full 10-octave MIDI range accessible
- **Velocity control** — adjustable via slider
- **Sustain pedal** — spacebar acts as sustain (CC#64)
- **Multi-key support** — play chords by holding multiple keys
- **Any MIDI port** — works with loopMIDI, internal MIDI, or hardware interfaces

## macOS / Linux

On macOS and Linux, `python-rtmidi` can create virtual ports directly (no loopMIDI needed).
Uncomment the virtual port code or use the built-in MIDI routing of your OS.

## Requirements

- Python 3.9+
- `python-rtmidi` (pip install)
- [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) (Windows only)
- tkinter (included with Python on Windows)

## License

MIT
