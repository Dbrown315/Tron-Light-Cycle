#
#  File: test_frame_builder.py
# Group: Group 9
# Purpose: Tests the frame builder properties.

import unittest
import numpy as np

from Game.engine import Engine
from Game.frame_builder import build_frame, COLORS
from Game.frame_builder import map_frame


class TestFrameBuilder(unittest.TestCase):
    def test_shape_and_dtype(self):
        f = build_frame(Engine())
        self.assertEqual(f.shape, (64, 64, 3))
        self.assertEqual(f.dtype, np.uint8)

    def test_positions_and_trails(self):
        e = Engine()
        e.step()
        f = build_frame(e)
        self.assertEqual(tuple(f[32, 17]), COLORS["blue"])
        self.assertTrue(f[32, 16].any())

    def test_duplicate_colors_rejected(self):
        with self.assertRaises(ValueError):
            build_frame(Engine(), ("white", "white"))


class TestMapBuilder(unittest.TestCase):
    def test_dimensions(self):
        frame = map_frame([])

        self.assertEqual(frame.shape, (64, 64, 3))

    def test_trail_rendering(self):
        players = [
            {
                "color": "blue",
                "trail": [(5, 5), (6, 5)],
                "position": (7, 5),
                "alive": True,
            }
        ]

        frame = map_frame(players)

        self.assertGreater(frame[5, 5, 2], 0)
        self.assertEqual(tuple(frame[5, 7]), (255, 255, 255))

    def test_out_of_bounds(self):
        players = [
            {
                "color": "red",
                "trail": [(-1, 5), (64, 5)],
                "position": (100, 100),
                "alive": True,
            }
        ]

        frame = map_frame(players)

        self.assertEqual(frame.sum(), 0)


if __name__ == "__main__":
    unittest.main()
