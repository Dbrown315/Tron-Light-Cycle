#
# File: input_router.py
# Group: Group 9
# Purpose: Translation of BLE events into session actions


PLAYERS = {"P1": 0, "P2": 1}
DIRECTIONS = {"UP", "DOWN", "LEFT", "RIGHT"}


def route_input(event, phase, navigation, steer):
    """
    Return selected GUI action or None; invoke steer(player, name) in play.

    During gameplay A/B do nothing.
    During menus, navigation handles directional focus and A selection while
    B is reserved for on-screen keyboard.
    """

    if not isinstance(event, (tuple, list)) or len(event) != 2:
        return None
    player_id, button = event
    if player_id not in PLAYERS or button not in DIRECTIONS | {"A", "B"}:
        return None
    if phase == "playing":
        if button in DIRECTIONS:
            steer(PLAYERS[player_id], button)
        return None
    return navigation.handle((player_id, button))
