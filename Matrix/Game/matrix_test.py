#
# File: matrix_test.py
# Group: Group 9
# Purpose: Independent matrix hardware test. Use Ctrl+C to stop.

import time
import numpy as np

try:
    from .matrix_renderer import MatrixRenderer
except ImportError:
    from matrix_renderer import MatrixRenderer


def main():
    renderer = MatrixRenderer()
    frame = np.zeros((64, 64, 3), dtype=np.uint8)
    # Dim patterns reduce glare and power use durinng first test
    frame[4:20, 4:20] = (40, 0, 0)
    frame[4:20, 24:40] = (0, 40, 0)
    frame[4:20, 44:60] = (0, 0, 40)
    frame[28:36, 28:36] = (35, 35, 35)
    try:
        renderer.show_pixels(frame)
        print("Displaying test pattern for 10 seconds...")
        time.sleep(10)
    finally:
        renderer.clear()


if __name__ == "__main__":
    main()
