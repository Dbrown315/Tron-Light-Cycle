#
# File: name_keyboard.py
# Group: Group 9
# Purpose: Display on-screen keyboard for name editing.

ROWS = (
    tuple("ABCDEFGHIJ"),
    tuple("KLMNOPQRST"),
    tuple("UVWXYZ0123"),
    tuple("456789") + ("SPACE", "DEL", "DONE", "CANCEL"),
)
MAX_NAME_LENGTH = 16


class NameKeyboard:
    def __init__(self, player, original):
        if player not in (0, 1):
            raise ValueError("player must be 0 or 1")
        self.player = player
        self.original = str(original)
        self.value = str(original)
        self.row = 0
        self.col = 0

    @property
    def selected(self):
        return ROWS[self.row][self.col]

    def handle(self, button):
        """
        Return "done", "cancel", or None.
        B removes the last character (backspace).
        """
        if button == "UP":
            self.row = (self.row - 1) % len(ROWS)
        elif button == "DOWN":
            self.row = (self.row + 1) % len(ROWS)
        elif button == "LEFT":
            self.col = (self.col - 1) % len(ROWS[self.row])
        elif button == "RIGHT":
            self.col = (self.col + 1) % len(ROWS[self.row])
        elif button == "B":
            self.value = self.value[:-1]
        elif button == "A":
            key = self.selected
            if key == "DONE":
                return "done"
            if key == "CANCEL":
                self.value = self.original
                return "cancel"
            if key == "DEL":
                self.value = self.value[:-1]
            elif len(self.value) < MAX_NAME_LENGTH:
                self.value += " " if key == "SPACE" else key
        return None

    def type_character(self, char):
        if (
            char
            and char.isprintable()
            and len(char) == 1
            and len(self.value) < MAX_NAME_LENGTH
        ):
            self.value += char
