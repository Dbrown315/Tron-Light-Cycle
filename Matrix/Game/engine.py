#
# File: engine.py
# Group: Group 9
# Purpose: Game engine for determining the game rules.

from dataclasses import dataclass
from enum import Enum

SIZE = 64


class Direction(Enum):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)


@dataclass
class Rider:
    pos: tuple[int, int]
    direction: Direction
    alive: bool = True


class Engine:
    def __init__(self, size=SIZE):
        self.size = size
        self.scores = [0, 0]
        self.round_number = 1
        self.reset_round()

    def reset_round(self):
        n = self.size
        self.riders = [
            Rider((n // 4, n // 2), Direction.RIGHT),
            Rider((3 * n // 4, n // 2), Direction.LEFT),
        ]
        self.trails = [{r.pos} for r in self.riders]
        self.finished = False
        self.winner = None  # None represents a draw for a round.

    def turn(self, player, direction):
        if (
            self.finished
            or player not in (0, 1)
            or not isinstance(direction, Direction)
        ):
            return False
        rider = self.riders[player]
        if not rider.alive:
            return False
        old = rider.direction.value
        new = direction.value
        if (old[0] + new[0], old[1] + new[1]) == (0, 0):
            return False
        rider.direction = direction
        return True

    def step(self):
        if self.finished:
            return self.winner
        destinations = []
        occupied = self.trails[0] | self.trails[1]
        crashed = [False, False]
        for i, rider in enumerate(self.riders):
            dx, dy = rider.direction.value
            x, y = rider.pos
            p = (x + dx, y + dy)
            destinations.append(p)
            crashed[i] = (
                not (0 <= p[0] < self.size and 0 <= p[1] < self.size) or p in occupied
            )
        if destinations[0] == destinations[1]:
            crashed = [True, True]
        for i, rider in enumerate(self.riders):
            rider.alive = not crashed[i]
            if rider.alive:
                rider.pos = destinations[i]
                self.trails[i].add(rider.pos)
        if any(crashed):
            self.finished = True
            if crashed[0] != crashed[1]:
                self.winner = 1 if crashed[0] else 0
                self.scores[self.winner] += 1
            self.round_number += 1
        return self.winner

    @property
    def match_winner(self):
        return next((i for i, score in enumerate(self.scores) if score >= 3), None)

    def next_round(self):
        if not self.finished or self.match_winner is not None:
            return False
        self.reset_round()
        return True

    def restart_match(self):
        self.scores = [0, 0]
        self.round_number = 1
        self.reset_round()
