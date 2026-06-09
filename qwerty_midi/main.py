"""QWERTY MIDI Keyboard — main application with tkinter GUI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .keymap import KEYMAP
from .midi_output import MidiOutput

# Maximum semitone offset in the keymap — used to bound octave shifting
MAX_KEY_OFFSET = max(KEYMAP.values())

# Piano visual constants
WHITE_KEY_WIDTH = 32
WHITE_KEY_HEIGHT = 140
BLACK_KEY_WIDTH = 20
BLACK_KEY_HEIGHT = 90
NUM_WHITE_KEYS = 24  # 2 octaves visible at a time

# Note names for display
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


class QwertyMidiApp:
    """Main application window."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("QWERTY MIDI Keyboard")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)

        self.midi = MidiOutput()
        self.base_note = 48  # C3 (middle-ish range)
        self.velocity = 100
        self.sustain_on = False
        self.active_notes: dict[str, int] = {}  # key → MIDI note number

        self._build_ui()
        self._bind_keys()
        self._refresh_ports()

    def _build_ui(self) -> None:
        """Build the full UI layout."""
        # Top control bar
        ctrl_frame = tk.Frame(self.root, bg="#16213e", pady=8, padx=12)
        ctrl_frame.pack(fill=tk.X)

        # MIDI port selection
        tk.Label(ctrl_frame, text="MIDI Port:", fg="#e0e0e0", bg="#16213e",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(ctrl_frame, textvariable=self.port_var,
                                       state="readonly", width=35)
        self.port_combo.pack(side=tk.LEFT, padx=(0, 8))

        self.connect_btn = tk.Button(ctrl_frame, text="Connect", command=self._connect_port,
                                     bg="#0f3460", fg="white", relief=tk.FLAT,
                                     font=("Segoe UI", 9, "bold"), padx=12)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 8))

        refresh_btn = tk.Button(ctrl_frame, text="Refresh", command=self._refresh_ports,
                                bg="#0f3460", fg="white", relief=tk.FLAT,
                                font=("Segoe UI", 9), padx=8)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 20))

        # Octave controls
        tk.Label(ctrl_frame, text="Octave:", fg="#e0e0e0", bg="#16213e",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))

        self.octave_label = tk.Label(ctrl_frame, text="C3", fg="#00d4ff", bg="#16213e",
                                     font=("Segoe UI", 12, "bold"), width=4)
        self.octave_label.pack(side=tk.LEFT)

        tk.Button(ctrl_frame, text="-", command=self._octave_down,
                  bg="#0f3460", fg="white", relief=tk.FLAT, width=3,
                  font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=2)
        tk.Button(ctrl_frame, text="+", command=self._octave_up,
                  bg="#0f3460", fg="white", relief=tk.FLAT, width=3,
                  font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(2, 20))

        # Velocity control
        tk.Label(ctrl_frame, text="Velocity:", fg="#e0e0e0", bg="#16213e",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))

        self.vel_var = tk.IntVar(value=self.velocity)
        vel_scale = ttk.Scale(ctrl_frame, from_=1, to=127, variable=self.vel_var,
                              orient=tk.HORIZONTAL, length=100,
                              command=self._velocity_changed)
        vel_scale.pack(side=tk.LEFT, padx=(0, 5))

        self.vel_label = tk.Label(ctrl_frame, text="100", fg="#00d4ff", bg="#16213e",
                                  font=("Segoe UI", 10, "bold"), width=4)
        self.vel_label.pack(side=tk.LEFT)

        # Status bar
        self.status_frame = tk.Frame(self.root, bg="#0a0a1a", pady=4, padx=12)
        self.status_frame.pack(fill=tk.X)

        self.status_label = tk.Label(self.status_frame, text="Not connected — select a MIDI port",
                                     fg="#ff6b6b", bg="#0a0a1a", font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT)

        self.sustain_label = tk.Label(self.status_frame, text="", fg="#ffd93d",
                                      bg="#0a0a1a", font=("Segoe UI", 9, "bold"))
        self.sustain_label.pack(side=tk.RIGHT)

        self.note_label = tk.Label(self.status_frame, text="", fg="#6bff6b",
                                   bg="#0a0a1a", font=("Segoe UI", 9))
        self.note_label.pack(side=tk.RIGHT, padx=(0, 20))

        # Piano canvas
        canvas_width = WHITE_KEY_WIDTH * NUM_WHITE_KEYS
        self.canvas = tk.Canvas(self.root, width=canvas_width, height=WHITE_KEY_HEIGHT + 40,
                                bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)

        # Key label hints
        hint_frame = tk.Frame(self.root, bg="#1a1a2e", pady=5)
        hint_frame.pack(fill=tk.X)

        hints = [
            ("Z-/ row", "Lower octave white keys"),
            ("S D G H J L ;", "Lower octave black keys"),
            ("Q-] row", "Upper octave white keys"),
            ("2 3 5 6 7 9 0 =", "Upper octave black keys"),
            ("Space", "Sustain pedal"),
            ("← →", "Octave shift"),
        ]
        for key, desc in hints:
            tk.Label(hint_frame, text=f"  {key}: {desc}",
                     fg="#888", bg="#1a1a2e", font=("Consolas", 9)).pack(side=tk.LEFT, padx=4)

        self._draw_piano()

    def _draw_piano(self) -> None:
        """Draw the piano keyboard visualization."""
        self.canvas.delete("all")
        self.white_key_rects: list[int] = []
        self.black_key_rects: list[int] = []

        # Draw white keys first
        for i in range(NUM_WHITE_KEYS):
            x = i * WHITE_KEY_WIDTH
            note_in_octave = self._white_key_note(i)
            midi_note = self.base_note + note_in_octave
            is_active = midi_note in self.active_notes.values()

            fill = "#4ecca3" if is_active else "#f0f0f0"
            outline = "#333"

            rect = self.canvas.create_rectangle(
                x, 0, x + WHITE_KEY_WIDTH, WHITE_KEY_HEIGHT,
                fill=fill, outline=outline, width=1
            )
            self.white_key_rects.append(rect)

            # Note name at bottom
            note_name = NOTE_NAMES[midi_note % 12]
            octave_num = midi_note // 12 - 1
            self.canvas.create_text(
                x + WHITE_KEY_WIDTH // 2, WHITE_KEY_HEIGHT - 15,
                text=f"{note_name}{octave_num}", fill="#555",
                font=("Consolas", 7)
            )

        # Draw black keys on top
        black_key_pattern = [1, 1, 0, 1, 1, 1, 0]  # C# D# _ F# G# A# _
        for i in range(NUM_WHITE_KEYS - 1):
            pattern_pos = i % 7
            if black_key_pattern[pattern_pos]:
                x = (i + 1) * WHITE_KEY_WIDTH - BLACK_KEY_WIDTH // 2
                # Determine midi note for this black key
                white_note = self._white_key_note(i)
                black_note_offset = white_note + 1
                midi_note = self.base_note + black_note_offset
                is_active = midi_note in self.active_notes.values()

                fill = "#ff6b6b" if is_active else "#1a1a2e"

                rect = self.canvas.create_rectangle(
                    x, 0, x + BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT,
                    fill=fill, outline="#000", width=1
                )
                self.black_key_rects.append(rect)

        # Draw keyboard mapping labels
        y_label = WHITE_KEY_HEIGHT + 10
        key_labels = self._get_visible_key_labels()
        for label_text, note_offset in key_labels:
            midi_note = self.base_note + note_offset
            is_black = NOTE_NAMES[midi_note % 12].endswith("#")
            # Find x position
            white_count = self._semitones_to_white_position(note_offset)
            if is_black:
                x = (white_count + 1) * WHITE_KEY_WIDTH
            else:
                x = white_count * WHITE_KEY_WIDTH + WHITE_KEY_WIDTH // 2

            if 0 <= x <= WHITE_KEY_WIDTH * NUM_WHITE_KEYS:
                self.canvas.create_text(
                    x, y_label + (12 if is_black else 0),
                    text=label_text.upper(), fill="#888" if not is_black else "#ff9999",
                    font=("Consolas", 8, "bold")
                )

    def _white_key_note(self, white_index: int) -> int:
        """Convert white key index to semitone offset."""
        white_to_semitone = [0, 2, 4, 5, 7, 9, 11]
        octave = white_index // 7
        position = white_index % 7
        return octave * 12 + white_to_semitone[position]

    def _semitones_to_white_position(self, semitones: int) -> int:
        """Convert semitone offset to approximate white key position."""
        semitone_to_white = {0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 3,
                            7: 4, 8: 4, 9: 5, 10: 5, 11: 6}
        octave = semitones // 12
        remainder = semitones % 12
        return octave * 7 + semitone_to_white[remainder]

    def _get_visible_key_labels(self) -> list[tuple[str, int]]:
        """Get key labels that map to visible notes."""
        labels = []
        for key, offset in KEYMAP.items():
            if 0 <= offset < NUM_WHITE_KEYS * 12 // 7:
                display = key if len(key) == 1 else key[0]
                labels.append((display, offset))
        return labels

    def _bind_keys(self) -> None:
        """Bind keyboard events."""
        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)
        self.root.focus_set()

    def _on_key_press(self, event: tk.Event) -> None:
        """Handle key press → MIDI Note On."""
        key = event.keysym.lower()

        # Octave shift
        if key == "left":
            self._octave_down()
            return
        if key == "right":
            self._octave_up()
            return

        # Sustain pedal
        if key == "space":
            if not self.sustain_on:
                self.sustain_on = True
                self.midi.sustain(True)
                self.sustain_label.config(text="SUSTAIN")
            return

        # Note keys
        if key in KEYMAP and key not in self.active_notes:
            offset = KEYMAP[key]
            midi_note = self.base_note + offset
            if 0 <= midi_note <= 127:
                self.active_notes[key] = midi_note
                self.midi.note_on(midi_note, self.velocity)
                note_name = NOTE_NAMES[midi_note % 12]
                octave_num = midi_note // 12 - 1
                self.note_label.config(text=f"{note_name}{octave_num} (MIDI {midi_note})")
                self._draw_piano()

    def _on_key_release(self, event: tk.Event) -> None:
        """Handle key release → MIDI Note Off."""
        key = event.keysym.lower()

        # Sustain release
        if key == "space":
            self.sustain_on = False
            self.midi.sustain(False)
            self.sustain_label.config(text="")
            return

        # Note keys
        if key in self.active_notes:
            midi_note = self.active_notes.pop(key)
            self.midi.note_off(midi_note)
            if not self.active_notes:
                self.note_label.config(text="")
            self._draw_piano()

    def _refresh_ports(self) -> None:
        """Refresh available MIDI ports."""
        ports = self.midi.available_ports
        self.port_combo["values"] = ports
        if ports:
            self.port_combo.current(0)

    def _connect_port(self) -> None:
        """Connect to selected MIDI port."""
        idx = self.port_combo.current()
        if idx < 0:
            self.status_label.config(text="No port selected", fg="#ff6b6b")
            return
        try:
            port_name = self.midi.open_port(idx)
            self.status_label.config(text=f"Connected: {port_name}", fg="#6bff6b")
            self.connect_btn.config(text="Connected", bg="#0a5e3a")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="#ff6b6b")

    def _octave_up(self) -> None:
        """Shift base note up one octave."""
        if self.base_note + 12 + MAX_KEY_OFFSET <= 127:
            self._release_all()
            self.base_note += 12
            self._update_octave_display()

    def _octave_down(self) -> None:
        """Shift base note down one octave."""
        if self.base_note > 0:
            self._release_all()
            self.base_note -= 12
            self._update_octave_display()

    def _update_octave_display(self) -> None:
        """Update octave label text."""
        note_name = NOTE_NAMES[self.base_note % 12]
        octave_num = self.base_note // 12 - 1
        self.octave_label.config(text=f"{note_name}{octave_num}")
        self._draw_piano()

    def _velocity_changed(self, value: str) -> None:
        """Handle velocity slider change."""
        self.velocity = int(float(value))
        self.vel_label.config(text=str(self.velocity))

    def _release_all(self) -> None:
        """Release all currently held notes."""
        for key, midi_note in list(self.active_notes.items()):
            self.midi.note_off(midi_note)
        self.active_notes.clear()
        self.midi.all_notes_off()

    def run(self) -> None:
        """Start the application main loop."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self) -> None:
        """Clean up on window close."""
        self._release_all()
        self.midi.close()
        self.root.destroy()


def main() -> None:
    """Entry point."""
    app = QwertyMidiApp()
    app.run()


if __name__ == "__main__":
    main()
