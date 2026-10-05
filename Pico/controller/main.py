from buttons import get_button_press
import time

counts = {
    "UP": 0,
    "DOWN": 0,
    "LEFT": 0,
    "RIGHT": 0
}

total = 0

while total < 20:
    direction = get_button_press()

    if direction is not None:
        counts[direction] += 1
        total += 1
        print(f"Button {direction} pressed. Total presses: {total}")

    time.sleep_ms(2)


print("\nTEST COMPLETE")

for direction, count in counts.items():
    print(f"{direction}: {count} presses")

print(f"Total presses: {total}")