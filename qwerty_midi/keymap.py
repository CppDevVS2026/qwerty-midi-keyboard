"""Keyboard-to-MIDI note mapping.

Uses a standard two-row piano layout:
  Lower row (Z-/ keys) → one octave of white+black keys
  Upper row (Q-] keys) → next octave of white+black keys

Offsets are semitones relative to the current base octave (C).
"""

# Lower row: maps keysym names → semitone offset from base note
# Layout mirrors a real piano: white keys on letter row, sharps on row above
LOWER_ROW = {
    # White keys (Z X C V B N M , . /)
    "z": 0,   # C
    "x": 2,   # D
    "c": 4,   # E
    "v": 5,   # F
    "b": 7,   # G
    "n": 9,   # A
    "m": 11,  # B
    "comma": 12,   # C+1
    "period": 14,  # D+1
    "slash": 16,   # E+1
    # Black keys (S D _ G H J _ L ;)
    "s": 1,   # C#
    "d": 3,   # D#
    "g": 6,   # F#
    "h": 8,   # G#
    "j": 10,  # A#
    "l": 13,  # C#+1
    "semicolon": 15,  # D#+1
}

# Upper row: one octave higher than lower row
UPPER_ROW = {
    # White keys (Q W E R T Y U I O P [ ])
    "q": 12,  # C
    "w": 14,  # D
    "e": 16,  # E
    "r": 17,  # F
    "t": 19,  # G
    "y": 21,  # A
    "u": 23,  # B
    "i": 24,  # C+1
    "o": 26,  # D+1
    "p": 28,  # E+1
    "bracketleft": 29,   # F+1
    "bracketright": 31,  # G+1
    # Black keys (2 3 _ 5 6 7 _ 9 0 _ = )
    "2": 13,  # C#
    "3": 15,  # D#
    "5": 18,  # F#
    "6": 20,  # G#
    "7": 22,  # A#
    "9": 25,  # C#+1
    "0": 27,  # D#+1
    "equal": 30,  # F#+1
}


def build_keymap() -> dict[str, int]:
    """Return combined keymap: keysym → semitone offset from base."""
    keymap: dict[str, int] = {}
    keymap.update(LOWER_ROW)
    keymap.update(UPPER_ROW)
    return keymap


# Pre-built for import convenience
KEYMAP = build_keymap()
