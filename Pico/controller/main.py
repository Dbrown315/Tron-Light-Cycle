
from ble_controller import send_button
from buttons import get_button_press
import time

while True:
    button = get_button_press()

    if button is not None:
        send_button(button)

    time.sleep_ms(2)
