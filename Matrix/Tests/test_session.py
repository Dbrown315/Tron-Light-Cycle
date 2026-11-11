#
# File: test_session.py
# Group: Group 9
# Purpose: Test criteria for a single game session

import unittest
from Game.engine import Direction
from Game.session import GameSession


class FakeRenderer:
    def __init__(self):
        self.frames = []
        self.cleared = False

    def show_pixels(self, pixels):
        self.frames.append(pixels.copy())

    def clear(self):
        self.cleared = True


class TestSession(unittest.TestCase):
    def test_start_and_tick(self):
        s = GameSession(ticks=10)
        self.assertTrue(s.start(0))
        self.assertEqual([e.kind for e in s.drain_events()], ["ROUND_STARTED"])
        pos = s.engine.riders[0].pos
        s.update(0.05)
        self.assertEqual(s.engine.riders[0].pos, pos)
        s.update(0.11)
        self.assertNotEqual(s.engine.riders[0].pos, pos)

    def test_round_result_and_next_round(self):
        s = GameSession(ticks=10)
        s.start(0)
        s.drain_events()
        # Force player 0 into wall while player 1 survives.
        s.engine.riders[0].pos = (0, 2)
        s.engine.riders[0].direction = Direction.LEFT
        s.engine.trails[0] = {(0, 2)}
        s.update(0.2)
        self.assertEqual(s.phase, "round_over")
        self.assertEqual(s.engine.scores, [0, 1])
        self.assertEqual([e.kind for e in s.drain_events()], ["ROUND_FINISHED"])
        self.assertTrue(s.start(0.3))
        self.assertEqual(s.engine.round_number, 2)

    def test_match_winner_and_reset(self):
        s = GameSession()
        s.engine.scores = [2, 0]
        s.start(0)
        s.engine.riders[1].pos = (63, 2)
        s.engine.riders[1].direction = Direction.RIGHT
        s.engine.trails[1] = {(63, 2)}
        s.update(1)
        self.assertEqual(s.phase, "match_over")
        self.assertEqual(s.engine.match_winner, 0)
        self.assertFalse(s.start(2))
        self.assertEqual(
            [e.kind for e in s.drain_events()],
            ["ROUND_STARTED", "ROUND_FINISHED", "MATCH_FINISHED"],
        )
        s.restart(3)
        self.assertEqual(s.engine.scores, [0, 0])

    def test_renderer(self):
        renderer = FakeRenderer()
        s = GameSession(renderer=renderer)
        s.show(0)
        self.assertEqual(renderer.frames[0].shape, (64, 64, 3))
        s.close()
        self.assertTrue(renderer.cleared)

    def test_distinct_colors(self):
        with self.assertRaises(ValueError):
            GameSession(colors=("blue", "blue"))


if __name__ == "__main__":
    unittest.main()
