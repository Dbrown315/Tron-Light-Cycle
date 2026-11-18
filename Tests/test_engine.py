#
# File: test_engine.py
# Group: Group 9
# Purpose: Test cases for game engine

import unittest
import numpy as np
from Game.engine import Engine, Direction
from Game.round_effects import result_frame


class EngineTests(unittest.TestCase):
    def test_no_reverse(self):
        e = Engine()
        self.assertFalse(e.turn(0, Direction.LEFT))
        self.assertTrue(e.turn(0, Direction.UP))

    def test_wall_collision(self):
        e = Engine()
        e.riders[0].pos = (0, 10)
        e.trails[0] = {(0, 10)}
        e.riders[0].direction = Direction.LEFT
        e.step()
        self.assertEqual(e.winner, 1)
        self.assertEqual(e.scores, [0, 1])

    def test_head_on_draw(self):
        e = Engine(size=8)
        e.riders[0].pos = (2, 2)
        e.riders[1].pos = (4, 2)
        e.trails = [{(2, 2)}, {(4, 2)}]
        e.step()
        self.assertTrue(e.finished)
        self.assertIsNone(e.winner)
        self.assertEqual(e.scores, [0, 0])

    def test_trail_collision(self):
        e = Engine()
        e.trails[0].add((17, 32))
        e.step()
        self.assertEqual(e.winner, 1)

    def test_match_winner(self):
        e = Engine()
        e.scores = [3, 1]
        self.assertEqual(e.match_winner, 0)
        self.assertFalse(e.next_round())


class EngineRefinementTests(unittest.TestCase):
    def test_one_turn_per_tick(self):
        e = Engine()
        self.assertTrue(e.turn(0, Direction.UP))
        self.assertFalse(e.turn(0, Direction.LEFT))
        self.assertEqual(e.riders[0].direction, Direction.UP)
        e.step()
        self.assertTrue(e.turn(0, Direction.LEFT))

    def test_no_reverse(self):
        e = Engine()
        self.assertFalse(e.turn(0, Direction.LEFT))
        self.assertTrue(e.turn(0, Direction.UP))

    def test_round_number_changes_on_next_round(self):
        e = Engine()
        while not e.finished:
            e.step()
        self.assertEqual(e.round_number, 1)
        self.assertTrue(e.next_round())
        self.assertEqual(e.round_number, 2)

    def test_effect_does_not_mutate_source(self):
        base = np.zeros((64, 64, 3), dtype=np.uint8)
        out = result_frame(base, 0, 0.0)
        self.assertGreater(out[0, 0].sum(), 0)
        self.assertEqual(base.sum(), 0)
        self.assertEqual(result_frame(base, None, 2.0).sum(), 0)


if __name__ == "__main__":
    unittest.main()
