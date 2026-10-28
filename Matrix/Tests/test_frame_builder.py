#
#  File: test_frame_builder.py
# Group: Group 9
# Purpose: Tests the frame builder properties.

import unittest

from Game.frame_builder import build_frame


class TestFrameBuilder(unittest.TestCase):
    def test_dimensions(self):
        frame = build_frame([])

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

        frame = build_frame(players)

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

        frame = build_frame(players)

        self.assertEqual(frame.sum(), 0)


if __name__ == "__main__":
    unittest.main()
