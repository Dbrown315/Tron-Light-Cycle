#
# File: test_stats_view.py
# Group: Group 9
# Purpose: Test cases for GUI leaderboard

import unittest
from GUI.stats_view import leaderboard_rows, metric_rows
from GUI.navigation import MenuNavigation


class StatsViewTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(leaderboard_rows([]), [])
        self.assertEqual(metric_rows({})[0], ("Rounds recorded", "0"))

    def test_leaderboard(self):
        rows = leaderboard_rows(
            [
                dict(
                    player="alice",
                    match_wins=3,
                    match_losses=1,
                    round_wins=9,
                    matches_played=4,
                )
            ]
        )
        self.assertEqual(rows, [("1", "alice", "3", "1", "9", "4")])

    def test_metrics_estimates_labeled(self):
        rows = metric_rows(dict(rounds=2, avg_round_ticks=8.5, draws=None))
        self.assertIn("Estimated", rows[3][0])
        self.assertEqual(rows[-1][1], "0")

    def test_controller_can_reach_stats_actions(self):
        n = MenuNavigation()
        n.set_phase("round_over")
        for _ in range(2):
            n.handle(("P1", "RIGHT"))
        self.assertEqual(n.handle(("P1", "A")), ("leaderboard",))
        n.handle(("P1", "RIGHT"))
        self.assertEqual(n.handle(("P1", "A")), ("telemetry",))
