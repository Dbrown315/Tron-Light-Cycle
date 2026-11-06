"""Headless GUI integration checks; no BLE hardware or real settings writes."""
import asyncio
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
try:
    import pygame
    from GUI import display
except ModuleNotFoundError as error:
    if error.name != 'pygame':
        raise
    pygame = None


@unittest.skipIf(pygame is None, 'Pygame is not installed')
class DisplayTests(unittest.IsolatedAsyncioTestCase):
    async def run_frames(self, commands=(), mouse_events=(), resize=False):
        queue = asyncio.Queue()
        for command in commands:
            queue.put_nowait(command)
        original_mode = pygame.display.set_mode
        def mode(size, flags=0):
            return original_mode((512, 300) if resize else size, flags)
        with patch.object(display, 'load_players', return_value=[
            p.copy() for p in display.DEFAULT_PLAYERS
        ]), patch.object(display, 'save_players') as save, patch.object(
            pygame.event, 'get', side_effect=[list(mouse_events),
                                             [pygame.event.Event(pygame.QUIT)]]
        ), patch.object(pygame.display, 'set_mode', side_effect=mode):
            try:
                await asyncio.wait_for(display.gui_loop(queue), 1)
                return save.call_args.args[0] if save.called else None
            finally:
                pygame.quit()

    async def test_controller_and_resized_mouse_dispatch_same_actions(self):
        controller = await self.run_frames(commands=[('P1', 'A'),
            ('P1', 'DOWN'), ('P1', 'DOWN'), ('P1', 'A')])
        mouse = await self.run_frames(mouse_events=[
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(36, 127)),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(30, 250)),
        ], resize=True)
        self.assertEqual(controller, mouse)
        self.assertEqual(controller[0]['character'], 'Butterfly')
        self.assertEqual(controller[1], display.DEFAULT_PLAYERS[1])

    async def test_restart_resets_focus_and_both_players(self):
        menu = display.MenuNavigation()
        with patch.object(display, 'MenuNavigation', return_value=menu):
            await self.run_frames(commands=[('P2', 'RIGHT'), ('P2', 'A'),
                ('P1', 'DOWN'), ('P1', 'DOWN'), ('P1', 'RIGHT'),
                ('P1', 'RIGHT'), ('P1', 'A')])
        self.assertEqual(menu.positions, [(0, 0), (0, 0)])

    async def test_ble_exit_stops_processing_and_cleans_up(self):
        stopped = asyncio.Event()
        async def receiver(queue):
            for button in ('DOWN', 'DOWN', 'RIGHT', 'RIGHT', 'RIGHT', 'A', 'A'):
                queue.put_nowait(('P2', button))
            try:
                await asyncio.Event().wait()
            finally:
                stopped.set()
        with patch.object(display, 'receive_controllers', side_effect=receiver), patch.object(
            display, 'load_players', return_value=[p.copy() for p in display.DEFAULT_PLAYERS]
        ), patch.object(pygame.event, 'get', return_value=[]), patch.object(
            display, 'save_players'
        ) as save:
            await asyncio.wait_for(display.run_gui(), 1)
        self.assertTrue(stopped.is_set())
        self.assertFalse(pygame.get_init())
        save.assert_not_called()

    async def test_keyboard_only_skips_receiver(self):
        with patch.object(display, 'receive_controllers') as receiver, patch.object(
            pygame.event, 'get', return_value=[pygame.event.Event(pygame.QUIT)]
        ):
            await display.run_gui(keyboard_only=True)
        receiver.assert_not_called()
        self.assertFalse(pygame.get_init())

    async def test_missing_ble_dependency_is_nonfatal(self):
        with patch.dict('sys.modules', bleak=None):
            await display.receive_controllers(asyncio.Queue())

    async def test_lowercase_saved_characters_are_normalized(self):
        data = [dict(p, character=p['character'].lower()) for p in display.DEFAULT_PLAYERS]
        with patch.object(Path, 'read_text', return_value=json.dumps(data)):
            self.assertEqual(display.load_players(), display.DEFAULT_PLAYERS)
