#
# File: session.py
# Group: Group 9
# Purpose: Maintain a single-process bridge between the GUI, engine, and
#          LED matrix.

from dataclasses import dataclass
from .engine import Direction, Engine
from .frame_builder import build_frame
from .round_effects import result_frame


@dataclass(frozen=True)
class GameEvent:
    kind: str
    round_number: int
    winner: int | None
    scores: tuple[int, int]
    match_winner: int | None


class GameSession:
    def __init__(self, colors=("white", "blue"), ticks=8, renderer=None):
        if len(colors) != 2 or colors[0] == colors[1]:
            raise ValueError("Players need distinct trail colors")
        if not 0 < ticks <= 30:
            raise ValueError("ticks must be in (0, 30]")
        self.engine = Engine()
        self.colors = tuple(colors)
        self.tick_interval = 1.0 / ticks
        self.renderer = renderer
        self.phase = "ready"  # ready, playing, round_over, match_over
        self.next_tick = None
        self.finished_at = None
        self.events = []

    def emit(self, kind):
        e = self.engine
        self.events.append(
            GameEvent(kind, e.round_number, e.winner, tuple(e.scores), e.match_winner)
        )

    def drain_events(self):
        events, self.events = self.events, []
        return events

    def start(self, now):
        if self.phase == "ready":
            self.phase = "playing"
            self.next_tick = now + self.tick_interval
            self.emit("ROUND_STARTED")
            return True
        if self.phase == "round_over" and self.engine.next_round():
            self.phase = "playing"
            self.finished_at = None
            self.next_tick = now + self.tick_interval
            self.emit("ROUND_STARTED")
            return True
        return False

    def steer(self, player, direction):
        return self.phase == "playing" and self.engine.turn(player, direction)

    def restart(self, now, colors=None):
        if colors is not None:
            if len(colors) != 2 or colors[0] == colors[1]:
                raise ValueError("Players need distinct trail colors")
            self.colors = tuple(colors)
        self.engine.restart_match()
        self.phase = "ready"
        self.next_tick = None
        self.finished_at = None
        self.emit("MATCH_RESET")

    def update(self, now):
        if self.phase != "playing" or now < self.next_tick:
            return
        # Exactly one engine movement per GUI iteration.
        self.engine.step()
        self.next_tick = now + self.tick_interval
        if self.engine.finished:
            self.finished_at = now
            self.phase = (
                "match_over" if self.engine.match_winner is not None else "round_over"
            )
            self.emit("ROUND_FINISHED")
            if self.phase == "match_over":
                self.emit("MATCH_FINISHED")

    def frame(self, now):
        pixels = build_frame(self.engine, self.colors)
        if self.finished_at is not None:
            pixels = result_frame(pixels, 
                                  self.engine.winner, 
                                  now - self.finished_at,
                                  colors=self.colors,
                                  )
        return pixels

    def show(self, now):
        if self.renderer is not None:
            self.renderer.show_pixels(self.frame(now))

    def close(self):
        if self.renderer is not None:
            self.renderer.clear()
