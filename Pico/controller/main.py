
from ble_controller import send_direction
from buttons import get_button_press
import time

while True:
    direction = get_button_press()

    if direction is not None:
        send_direction(direction)

    time.sleep_ms(2)
