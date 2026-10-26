#
# File: test_engine.py
# Group: Group 9
# Purpose: Test cases for game engine

import unittest
from Game.engine import Engine, Direction


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


if __name__ == "__main__":
    unittest.main()
