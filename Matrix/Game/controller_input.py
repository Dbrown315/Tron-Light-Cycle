"""Translate normalized BLE commands without coupling the engine to Bluetooth."""

try:
    from .engine import Direction
except ImportError:
    from engine import Direction

PLAYERS = {"P1": 0, "P2": 1}


def advance_round(engine):
    """Advance a finished round or restart a completed match; report a change."""
    if not engine.finished:
        return False
    if engine.match_winner is not None:
        engine.restart_match()
        return True
    return engine.next_round()


def drain_controller_inputs(engine, input_queue, *, discard=False,
                            discard_directions=False):
    """Consume this frame's commands and report whether A started a round.

    Directions from a finished round must not steer a newly started round,
    including when Space has already advanced it during this frame.
    """
    discard_directions = discard_directions or engine.finished
    advanced = False
    for _ in range(input_queue.qsize()):
        event = input_queue.get_nowait()
        try:
            if discard:
                continue
            if not isinstance(event, (tuple, list)) or len(event) != 2:
                continue
            player, button = event
            if not isinstance(player, str) or not isinstance(button, str):
                continue
            if player not in PLAYERS:
                continue
            if button == "A":
                advanced = advance_round(engine) or advanced
            elif not discard_directions and button in Direction.__members__:
                engine.turn(PLAYERS[player], Direction[button])
            # B is transported and acknowledged but has no game action yet.
        finally:
            input_queue.task_done()
    return advanced
