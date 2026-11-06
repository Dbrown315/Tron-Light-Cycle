import unittest

from GUI.navigation import MenuNavigation


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.menu = MenuNavigation()

    def test_independent_focus_and_player_ownership(self):
        self.assertEqual(self.menu.handle(('P1', 'A')), ('char_prev', 0))
        self.assertEqual(self.menu.handle(('P2', 'A')), ('char_prev', 1))
        self.menu.handle(('P1', 'RIGHT'))
        self.menu.handle(('P1', 'DOWN'))
        self.assertEqual(self.menu.handle(('P1', 'A')), ('color_next', 0))
        self.assertEqual(self.menu.handle(('P2', 'A')), ('char_prev', 1))

    def test_boundaries_and_row_column_clamping(self):
        for _ in range(5):
            self.menu.handle(('P1', 'UP'))
            self.menu.handle(('P1', 'LEFT'))
        self.assertEqual(self.menu.positions[0], (0, 0))
        for _ in range(5):
            self.menu.handle(('P1', 'RIGHT'))
        self.assertEqual(self.menu.positions[0], (0, 1))
        self.menu.handle(('P1', 'DOWN'))
        self.assertEqual(self.menu.positions[0], (1, 1))
        for _ in range(5):
            self.menu.handle(('P1', 'DOWN'))
            self.menu.handle(('P1', 'RIGHT'))
        self.assertEqual(self.menu.handle(('P1', 'A')), ('exit',))
        self.menu.handle(('P1', 'UP'))
        self.assertEqual(self.menu.handle(('P1', 'A')), ('color_next', 0))

    def test_shared_controls_and_coincident_focus(self):
        for player in ('P1', 'P2'):
            self.menu.handle((player, 'DOWN'))
            self.menu.handle((player, 'DOWN'))
        for action in ('start', 'play_again', 'restart', 'exit'):
            for player in ('P1', 'P2'):
                self.assertEqual(self.menu.handle((player, 'A')), (action,))
                self.menu.handle((player, 'RIGHT'))

    def test_b_and_malformed_events_do_nothing(self):
        for event in (None, (), ('P3', 'A'), ([], {}), ('P1', 'B'), ('P1', 'BAD')):
            self.assertIsNone(self.menu.handle(event))
        self.assertEqual(self.menu.positions, [(0, 0), (0, 0)])

    def test_reset_restores_both_players(self):
        self.menu.handle(('P1', 'DOWN'))
        self.menu.handle(('P2', 'RIGHT'))
        self.menu.reset()
        self.assertEqual(self.menu.positions, [(0, 0), (0, 0)])
