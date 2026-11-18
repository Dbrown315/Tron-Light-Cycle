#
# File: test_telemetry.py
# Group: Group 9
# Purpose: Test cases for game telemetry

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from Game.telemetry import TelemetryRecorder


def event(kind, number=1, winner=None, scores=(0, 0), match_winner=None):
    return SimpleNamespace(
        kind=kind,
        round_number=number,
        winner=winner,
        scores=scores,
        match_winner=match_winner,
    )


class TelemetryTests(unittest.TestCase):
    def test_match_and_round_persist(self):
        with tempfile.TemporaryDirectory() as directory:
            t = [100.0]
            r = TelemetryRecorder(Path(directory) / "stats.sqlite3", clock=lambda: t[0])
            session = SimpleNamespace(
                engine=SimpleNamespace(trails=[{(1, 1)}, {(2, 2)}])
            )
            r.observe(session, [event("ROUND_STARTED")], ["Alice", "Bob"])
            t[0] += 4
            session.engine.trails = [set(range(12)), set(range(8))]
            r.observe(
                session,
                [event("ROUND_FINISHED", winner=0, scores=(1, 0))],
                ["Alice", "Bob"],
            )
            r.observe(session, [event("ROUND_STARTED", number=2)], ["Alice", "Bob"])
            r.observe(
                session,
                [event("ROUND_FINISHED", number=2, winner=0, scores=(2, 0))],
                ["Alice", "Bob"],
            )
            r.observe(session, [event("ROUND_STARTED", number=3)], ["Alice", "Bob"])
            r.observe(
                session,
                [
                    event("ROUND_FINISHED", number=3, winner=0, scores=(3, 0)),
                    event(
                        "MATCH_FINISHED",
                        number=3,
                        winner=0,
                        scores=(3, 0),
                        match_winner=0,
                    ),
                ],
                ["Alice", "Bob"],
            )
            self.assertEqual(r.leaderboard()[0]["player"], "alice")
            self.assertEqual(r.leaderboard()[0]["match_wins"], 1)
            self.assertEqual(r.leaderboard()[0]["round_wins"], 3)
            self.assertEqual(r.metrics()["rounds"], 3)
            r.close()
            r2 = TelemetryRecorder(Path(directory) / "stats.sqlite3")
            self.assertEqual(r2.leaderboard()[0]["match_wins"], 1)
            r2.close()

    def test_abandoned_match_does_not_count_as_completed(self):
        with tempfile.TemporaryDirectory() as directory:
            r = TelemetryRecorder(Path(directory) / "stats.sqlite3")
            session = SimpleNamespace(engine=SimpleNamespace(trails=[{1}, {2}]))
            r.observe(
                session, [event("ROUND_STARTED"), event("MATCH_RESET")], ["A", "B"]
            )
            self.assertEqual(r.leaderboard(), [])
            r.close()


if __name__ == "__main__":
    unittest.main()
