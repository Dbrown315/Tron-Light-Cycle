#
# File: round_effects.py
# Group: Group 9
# Purpose: Feedback from RGB matrix after a round ends.

import numpy as np
from .frame_builder import COLORS


def result_frame(base_frame, winner, elapsed, colors=("blue", "orange")):
    """
    Pulse a border for 1.5s; winner 0/1, or None for a draw.
    """
    frame = np.array(base_frame, copy=True)
    if elapsed < 0 or elapsed >= 1.5:
        return frame
    if int(elapsed * 5) % 2:
        return frame
    border = (
        COLORS[colors[winner]]
        if winner in (0,1)
        else (160, 160, 160)
    )
    frame[0, :, :] = border
    frame[-1, :, :] = border
    frame[:, 0, :] = border
    frame[:, -1, :] = border
    return frame
