#
# File: test_input_router.py
# Group: Group 9
# Purpose: Test input routing

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "Matrix"), str(ROOT / "GUI")]
from Game.input_router import route_input
from navigation import MenuNavigation


class TestInputRouter(unittest.TestCase):
    def setUp(self):
        self.nav = MenuNavigation()
        self.steered = []
        self.steer = lambda player, direction: self.steered.append((player, direction))

    def test_two_player_steering(self):
        route_input(("P1", "LEFT"), "playing", self.nav, self.steer)
        route_input(("P2", "RIGHT"), "playing", self.nav, self.steer)
        self.assertEqual(self.steered, [(0, "LEFT"), (1, "RIGHT")])

    def test_no_menu_actions_during_game(self):
        self.assertIsNone(route_input(("P1", "A"), "playing", self.nav, self.steer))

    def test_setup_selection(self):
        self.assertEqual(
            route_input(("P1", "A"), "ready", self.nav, self.steer), ("char_prev", 0)
        )
        route_input(("P2", "RIGHT"), "ready", self.nav, self.steer)
        self.assertEqual(
            route_input(("P2", "A"), "ready", self.nav, self.steer), ("char_next", 1)
        )

    def test_round_advance_selection(self):
        self.nav.set_phase("round_over")
        self.assertEqual(
            route_input(("P1", "A"), "round_over", self.nav, self.steer),
            ("play_again",),
        )

    def test_invalid_packets(self):
        for event in [("P3", "UP"), ("P1", "BOGUS"), ("P1",), None]:
            self.assertIsNone(route_input(event, "playing", self.nav, self.steer))
        self.assertEqual(self.steered, [])

    def test_b_reserved(self):
        self.assertIsNone(route_input(("P1", "B"), "ready", self.nav, self.steer))


if __name__ == "__main__":
    unittest.main()
