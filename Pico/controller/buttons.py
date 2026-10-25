from machine import Pin
import time
from config import SETTINGS

# Change number to match GPIO pin number. Does not go by physical pin number on the board.
BUTTONS = {
    "UP": Pin(int(SETTINGS["GPIO_UP"]), Pin.IN, Pin.PULL_UP),
    "DOWN": Pin(int(SETTINGS["GPIO_DOWN"]), Pin.IN, Pin.PULL_UP),
    "LEFT": Pin(int(SETTINGS["GPIO_LEFT"]), Pin.IN, Pin.PULL_UP),
    "RIGHT": Pin(int(SETTINGS["GPIO_RIGHT"]), Pin.IN, Pin.PULL_UP),
}

DEBOUNCE_TIME = 20  # ms

# Track a stable state and a candidate state for each active-low button.
_now = time.ticks_ms()
_states = {}
for _name, _pin in BUTTONS.items():
    _raw = _pin.value()
    _states[_name] = {
        "stable": 1,
        "candidate": _raw,
        "changed_at": _now,
    }


def get_button_press():
    """Return a button name once its press is debounced, without blocking."""
    now = time.ticks_ms()
    for name, pin in BUTTONS.items():
        state = _states[name]
        raw = pin.value()

        if raw != state["candidate"]:
            state["candidate"] = raw
            state["changed_at"] = now
        elif (raw != state["stable"] and
              time.ticks_diff(now, state["changed_at"]) >= DEBOUNCE_TIME):
            state["stable"] = raw
            if raw == 0:
                return name

    return None
