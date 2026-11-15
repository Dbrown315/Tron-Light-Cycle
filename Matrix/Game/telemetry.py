#
# File: telemetry.py
# Group: Group 9
# Purpose: Implement game play telemetry to observe game metrics.

import json
import sqlite3
import time
import uuid
from pathlib import Path


class TelemetryRecorder:
    def __init__(self, database, clock=time.time):
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self.clock = clock
        self.connection = sqlite3.connect(str(self.database))
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS matches(
                id TEXT PRIMARY KEY, started_at REAL NOT NULL,
                ended_at REAL, player1 TEXT NOT NULL, player2 TEXT NOT NULL,
                winner INTEGER, status TEXT NOT NULL DEFAULT "active"
            );
            CREATE TABLE IF NOT EXISTS rounds(
                match_id TEXT NOT NULL REFERENCES matches(id),
                round_number INTEGER NOT NULL, winner INTEGER,
                duration_seconds REAL NOT NULL, ticks INTEGER NOT NULL,
                p1_trail_cells INTEGER NOT NULL, p2_trail_cells INTEGER NOT NULL,
                p1_score INTEGER NOT NULL, p2_score INTEGER NOT NULL,
                PRIMARY KEY(match_id, round_number)
            );
        """)
        self.connection.commit()
        self.match_id = None
        self.round_started = None
        self.round_ticks = 0
        self._previous_trail_sizes = None

    def observe(self, session, events, names):
        """
        Consume GameEvent instances once, in order; names is a two-element sequence.
        """
        if len(names) != 2:
            raise ValueError("Exactly two player names are required.")
        for event in events:
            if event.kind == "MATCH_RESET":
                self._abandon()
            elif event.kind == "ROUND_STARTED":
                if self.match_id is None:
                    self.match_id = uuid.uuid4().hex
                    self.connection.execute(
                        "INSERT IINTO matches(id, started_at, player1, player2) VALUES(?, ?, ?, ?)",
                        (self.match_id, self.clock(), str(names[0]), str(names[1])),
                    )
                self.round_started = self.clock()
                self.round_ticks = 0
                self._previous_trail_sizes = tuple(
                    len(t) for t in session.engine.trails
                )
            elif (
                event.kind == "ROUND_FINISHED"
                and self.match_id is not None
                and self.round_started is not None
            ):
                e = session.engine
                trail_sizes = tuple(len(t) for t in e.trails)
                self.connection.execute(
                    """ INSERT OR IGNORE INTO rounds
                    (match_id, round_number, winner, duration_seconds, ticks, p1_trail_cells, p2_trail_cells, p1_score, p2_score)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        self.match_id,
                        event.round_number,
                        event.winner,
                        max(0.0, self.clock() - self.round_started),
                        max(self.round_ticks, max(trail_sizes) - 1),
                        trail_sizes[0],
                        trail_sizes[1],
                        event.scores[0],
                        event.scores[1],
                    ),
                )
                self.round_started = None
            elif event.kind == "MATCH_FINISHED" and self.match_id is not None:
                self.connection.execute(
                    """ UPDATE matches SET ended_at=?, winner=?, status="complete"
                    WHERE id=?""",
                    (self.clock(), event.match_winner, self.match_id),
                )
                self.match_id = None
                self.round_started = None
            self.connection.commit()

    def _abandon(self):
        if self.match_id is not None:
            self.connection.execute(
                "UPDATE matches SET status='abandoned', ended_at=? WHERE id=?",
                (self.clock(), self.match_id),
            )
            self.connection.commit()
        self.match_id = None
        self.round_started = None

    def leaderboard(self, limit=20):
        """
        Rank players by completed match wins, then round wins, then name.
        Names are case-insensitive identities; repeated names are combined.
        """
        rows = self.connection.execute(
            """  
            WITH participants AS (
            SELECT lower(trim(player1)) AS player, id, 0 AS seat, winner, status FROM matches
            UNION ALL
            SELECT lower(trim(player2)), id, 1, winner, status FROM matches
            ), results AS(
                SELECT player,
                        SUM(CASE WHEN status="complete" THEN 1 ELSE 0 END) AS matches_played,
                        SUM(CASE WHEN status="complete" AND winner=seat THEN 1 ELSE 0 END) AS match_wins,
                        SUM(CASE WHEN status="complete" AND winner IS NOT NULL AND winner!=seat THEN 1 ELSE 0 END) AS match_losses,
                        SUM(CASE WHEN status="complete" AND winner IS NULL THEN  1 ELSE 0 END) AS match_draws
                FROM participants GROUP BY player
            ), round_results AS(
                SELECT p.player, SUM(CASE WHEN r.winner=p.seat THEN 1 ELSE 0 END) AS round_wins,
                        COUNT(r.round_number) AS rounds_played
                FROM participants p JOIN rounds r ON r.match_id=p.id
                GROUP BY p.player
            )
            SELECT results.player, matches_played, match_wins, match_losses, match_draws,
                    COALESCE(round_wins, 0), COALESCE(rounds_played, 0)
            FROM results LEFT JOIN round_results USING(player)
            WHERE matches_played > 0
            ORDER BY match_wins DESC, round_wins DESC, results.player ASC LIMIT ?
        """,
            (max(1, int(limit)),),
        ).fetchall()
        fields = (
            "player",
            "matches_played",
            "match_wins",
            "match_losses",
            "match_draws",
            "round_wins",
            "rounds_played",
        )
        return [dict(zip(fields, row)) for row in rows]

    def metrics(self):
        row = self.connection.execute(
            """SELECT COUNT(*), COALESCE(AVG(duration_seconds),0),
            COALESCE(MAX(duration_seconds),0), COALESCE(AVG(ticks),0),
            COALESCE(AVG(p1_trail_cells+p2_trail_cells),0),
            SUM(CASE WHEN winner IS NULL THEN 1 ELSE 0 END)
            FROM rounds"""
        ).fetchone()
        return dict(
            zip(
                (
                    "rounds",
                    "avg_round_seconds",
                    "longest_round_seconds",
                    "avg_round_ticks",
                    "avg_combined_trail_cells",
                    "draws",
                ),
                row,
            )
        )

    def close(self):
        self.connection.close()
