#
# File: test_name_keyboard.py
# Group: Group 9
# Purpose: Test on-screen keyboard controls

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "GUI"))
from name_keyboard import NameKeyboard, ROWS


class NameKeyboardTests(unittest.TestCase):
    def test_select_and_limit(self):
        editor = NameKeyboard(0, "")
        for _ in range(20):
            editor.handle("A")
        self.assertEqual(editor.value, "A" * 16)

    def test_independent_player(self):
        editor = NameKeyboard(1, "P2")
        self.assertEqual(editor.player, 1)
        editor.handle("B")
        self.assertEqual(editor.value, "P")

    def test_cancel_restores(self):
        editor = NameKeyboard(0, "Original")
        editor.handle("B")
        editor.row, editor.col = 3, 9
        self.assertEqual(editor.handle("A"), "cancel")
        self.assertEqual(editor.value, "Original")

    def test_done(self):
        editor = NameKeyboard(0, "Ada")
        editor.row, editor.col = 3, 8
        self.assertEqual(editor.handle("A"), "done")
        self.assertEqual(editor.value, "Ada")

    def test_wrap_and_space(self):
        editor = NameKeyboard(0, "A")
        editor.handle("UP")
        self.assertEqual(editor.row, 3)
        editor.row, editor.col = 3, 6
        editor.handle("A")
        self.assertEqual(editor.value, "A ")
        editor.handle("RIGHT")
        editor.handle("A")
        self.assertEqual(editor.value, "A")

    def test_physical_input(self):
        editor = NameKeyboard(0, "")
        editor.type_character("é")
        editor.type_character("\n")
        self.assertEqual(editor.value, "é")

    def test_layout_is_rectangular(self):
        self.assertEqual([len(row) for row in ROWS], [10, 10, 10, 10])


if __name__ == "__main__":
    unittest.main()
