"""Independent controller focus for the existing GUI button actions."""

PLAYERS = {"P1": 0, "P2": 1}
SHARED_ACTIONS = (("start",), ("play_again",), ("restart",), ("exit",))


class MenuNavigation:
    def __init__(self):
        self.reset()

    def reset(self):
        self.positions = [(0, 0), (0, 0)]

    def selected_action(self, player):
        row, column = self.positions[player]
        if row == 2:
            return SHARED_ACTIONS[column]
        kind = (("char_prev", "char_next"), ("color_prev", "color_next"))[row][column]
        return kind, player

    def handle(self, event):
        """Move focus, or return the action selected with A. Ignore other input."""
        if not isinstance(event, (tuple, list)) or len(event) != 2:
            return None
        player_id, button = event
        if not isinstance(player_id, str) or not isinstance(button, str):
            return None
        if player_id not in PLAYERS:
            return None
        player = PLAYERS[player_id]
        if button == "A":
            return self.selected_action(player)
        row, column = self.positions[player]
        if button == "UP":
            row = max(0, row - 1)
        elif button == "DOWN":
            row = min(2, row + 1)
        elif button == "LEFT":
            column = max(0, column - 1)
        elif button == "RIGHT":
            column += 1
        else:
            return None
        column = min(column, 3 if row == 2 else 1)
        self.positions[player] = row, column
        return None
