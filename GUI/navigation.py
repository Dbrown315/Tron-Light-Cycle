#
# File: navigation.py
# Group: Group 9
# Purpose: Independent Player(P1/P2) controller focus for GUI.

PLAYERS = {"P1": 0, "P2": 1}
SHARED = [
    ("start",),
    ("play_again",),
    ("restart",),
    ("leaderboard",),
    ("telemetry",),
    ("exit",),
]


class MenuNavigation:
    def __init__(self):
        self.reset()

    def reset(self):
        self.positions = [(1, 0), (1, 0)]
        self.phase = "ready"

    def set_phase(self, phase):
        if phase != self.phase:
            self.phase = phase
            if phase in ("round_over", "match_over"):
                self.positions = [(2, 1), (2, 1)]
            elif phase == "ready":
                self.positions = [(1, 0), (1, 0)]

    def selected_action(self, player):
        row, col = self.positions[player]
        if row == 2:
            return SHARED[col]
        if row == 0:
            return ("edit_name", player)
        return (("color_prev", "color_next")[col], player)

    def handle(self, event):
        if not isinstance(event, (tuple, list)) or len(event) != 2:
            return None
        player_id, button = event
        if player_id not in PLAYERS or not isinstance(button, str):
            return None
        player = PLAYERS[player_id]
        if button == "A":
            return self.selected_action(player)
        if button not in ("UP", "DOWN", "LEFT", "RIGHT"):
            return None
        row, col = self.positions[player]
        if self.phase != "ready":
            row = 2
        elif button == "UP":
            row = max(0, row - 1)
        elif button == "DOWN":
            row = min(2, row + 1)
        if button == "LEFT":
            col = max(0, col - 1)
        elif button == "RIGHT":
            col = min(len(SHARED) - 1 if row == 2 else 1, col + 1)
        col = min(col, len(SHARED) - 1 if row == 2 else 1)
        if row == 0:
            col = 0
        self.positions[player] = row, col
        return None
