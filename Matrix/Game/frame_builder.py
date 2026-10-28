#
# File: frame_builder.py
# Group: Group 9
# Purpose: Convert a game state into a 64x64 RGB frame.

import numpy as np

WIDTH = 64
HEIGHT = 64

TRAIL_COLORS = {
    "red": (255, 50, 65),
    "orange": (255, 145, 40),
    "yellow": (255, 220, 55),
    "green": (45, 255, 110),
    "blue": (45, 160, 255),
    "indigo": (95, 80, 255),
    "violet": (190, 80, 255),
    "white": (220, 220, 220),
}


def build_frame(players, brightness=0.35):
    """
    Create an RGB frame from player state.

    Each player is a dictionary containing:
        color: color name e.g. red, blue, etc.
        trail: iterable of (x, y) positions
        position: current (x, y) position
        alive: bool

    Coordinates use (x, y) with (0, 0) at top-left.
    """

    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    brightness = max(0.0, min(1.0, brightness))

    # Draw persistent trails
    for player in players:
        color = TRAIL_COLORS[player["color"]]
        dimmed = tuple(int(c * brightness) for c in color)

        for x, y in player["trail"]:
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                frame[y, x] = dimmed

    # Draw cycle heads above their trails
    for player in players:
        if not player["alive"]:
            continue

        x, y = player["position"]

        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            frame[y, x] = (255, 255, 255)

    return frame
