"""MIDI output via python-rtmidi."""

from __future__ import annotations

import rtmidi


class MidiOutput:
    """Manages a MIDI output port connection."""

    NOTE_ON = 0x90
    NOTE_OFF = 0x80
    CONTROL_CHANGE = 0xB0
    SUSTAIN_CC = 64

    def __init__(self) -> None:
        self._midi_out = rtmidi.MidiOut()
        self._port_index: int | None = None

    @property
    def available_ports(self) -> list[str]:
        """List available MIDI output port names."""
        return self._midi_out.get_ports()

    @property
    def is_connected(self) -> bool:
        return self._midi_out.is_port_open()

    def open_port(self, index: int) -> str:
        """Open a MIDI output port by index. Returns port name."""
        if self._midi_out.is_port_open():
            self._midi_out.close_port()
        ports = self.available_ports
        if index < 0 or index >= len(ports):
            raise ValueError(f"Port index {index} out of range (0-{len(ports) - 1})")
        self._midi_out.open_port(index)
        self._port_index = index
        return ports[index]

    def open_virtual_port(self, name: str = "QWERTY MIDI Keyboard") -> None:
        """Open a virtual MIDI port (macOS/Linux). On Windows, use loopMIDI instead."""
        self._midi_out.open_virtual_port(name)

    def close(self) -> None:
        """Close the MIDI port."""
        if self._midi_out.is_port_open():
            self._midi_out.close_port()

    def note_on(self, note: int, velocity: int = 100, channel: int = 0) -> None:
        """Send a MIDI Note On message."""
        note = max(0, min(127, note))
        velocity = max(0, min(127, velocity))
        self._midi_out.send_message([self.NOTE_ON | channel, note, velocity])

    def note_off(self, note: int, channel: int = 0) -> None:
        """Send a MIDI Note Off message."""
        note = max(0, min(127, note))
        self._midi_out.send_message([self.NOTE_OFF | channel, note, 0])

    def sustain(self, on: bool, channel: int = 0) -> None:
        """Send sustain pedal CC message."""
        value = 127 if on else 0
        self._midi_out.send_message([self.CONTROL_CHANGE | channel, self.SUSTAIN_CC, value])

    def all_notes_off(self, channel: int = 0) -> None:
        """Send All Notes Off CC (CC#123)."""
        self._midi_out.send_message([self.CONTROL_CHANGE | channel, 123, 0])
