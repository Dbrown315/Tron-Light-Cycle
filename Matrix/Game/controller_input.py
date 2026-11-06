"""Translate normalized BLE commands without coupling the engine to Bluetooth."""

try:
    from .engine import Direction
except ImportError:
    from engine import Direction

PLAYERS = {"P1": 0, "P2": 1}


def drain_controller_inputs(engine, input_queue, *, discard=False):
    """Consume this frame's pending commands in order on the game thread."""
    for _ in range(input_queue.qsize()):
        event = input_queue.get_nowait()
        try:
            if discard or engine.finished:
                continue
            if not isinstance(event, (tuple, list)) or len(event) != 2:
                continue
            player, direction = event
            if not isinstance(player, str) or not isinstance(direction, str):
                continue
            if player in PLAYERS and direction in Direction.__members__:
                engine.turn(PLAYERS[player], Direction[direction])
        finally:
            input_queue.task_done()
