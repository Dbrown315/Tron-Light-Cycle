from machine import Pin
import time

BUTTONS = {
    "UP": Pin(0, Pin.IN, Pin.PULL_UP),
    "DOWN": Pin(1, Pin.IN, Pin.PULL_UP),
    "LEFT": Pin(2, Pin.IN, Pin.PULL_UP),
    "RIGHT": Pin(3, Pin.IN, Pin.PULL_UP),
}

DEBOUNCE_TIME = 50 # ms

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
