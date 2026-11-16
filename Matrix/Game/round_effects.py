
#
# File: round_effects.py
# Group: Group 9
# Purpose: Feedback from RGB matrix after a round ends.

import numpy as np
from .frame_builder import COLORS


def result_frame(base_frame, winner, elapsed, colors=("blue", "orange")):
    """
    Pulse a border for 1.5 seconds after a round ends.

    Winner:
        0 or 1 - Flash the winning player's selected color.
        None   - Flash a red-and-white striped border for a tie.
    """
    frame = np.array(base_frame, copy=True)

    # Stop the effect after 1.5 seconds.
    if elapsed < 0 or elapsed >= 1.5:
        return frame

    # Blink the border on and off.
    if int(elapsed * 5) % 2:
        return frame

    if winner is None:
        # Red-and-white striped border for ties.
        red = (255, 50, 50)
        white = (255, 255, 255)

        # Top and bottom borders.
        for x in range(frame.shape[1]):
            color = red if (x // 4) % 2 == 0 else white
            frame[0, x] = color
            frame[-1, x] = color

        # Left and right borders.
        for y in range(frame.shape[0]):
            color = red if (y // 4) % 2 == 0 else white
            frame[y, 0] = color
            frame[y, -1] = color

    else:
        # Solid border matching the round winner's color.
        border = COLORS[colors[winner]]

        frame[0, :, :] = border
        frame[-1, :, :] = border
        frame[:, 0, :] = border
        frame[:, -1, :] = border

    return frame
