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

DEBOUNCE_TIME = 50 # ms

# Returns the name of the button pressed, or None if no button is pressed.
def get_button_press():
    for name, pin in BUTTONS.items():
        if pin.value() == 0: 
            time.sleep_ms(DEBOUNCE_TIME)
            if pin.value() == 0:
                while pin.value() == 0:
                    time.sleep_ms(5)

                time.sleep_ms(DEBOUNCE_TIME)

                return name
    return None
