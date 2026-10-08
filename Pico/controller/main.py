from buttons import get_button_press
import time

# This script tests the button press functionality. It counts the number of times each button is pressed until a total of 20 presses is reached.
counts = {
    "UP": 0,
    "DOWN": 0,
    "LEFT": 0,
    "RIGHT": 0
}

total = 0

# Wait for the user to press buttons until a total of 20 presses is reached.
while total < 20:
    direction = get_button_press()

    # If a button was pressed, increment the count for that button and the total count.
    if direction is not None:
        counts[direction] += 1
        total += 1
        print(f"Button {direction} pressed. Total presses: {total}")

    time.sleep_ms(2)


print("\nTEST COMPLETE")

for direction, count in counts.items():
    print(f"{direction}: {count} presses")

print(f"Total presses: {total}")