"""Headless simulator checks; require Pygame but no display or Bluetooth."""
import asyncio
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
try:
    import pygame
    from Game import simulator
except ModuleNotFoundError as error:
    if error.name != "pygame":
        raise
    pygame = None


@unittest.skipIf(pygame is None, "Pygame is not installed")
class SimulatorTests(unittest.IsolatedAsyncioTestCase):
    async def play(self, keyboard_only):
        engine = simulator.Engine()
        stopped = asyncio.Event()
        receiver_started = False

        async def receiver(queue):
            nonlocal receiver_started
            receiver_started = True
            queue.put_nowait(("P2", "DOWN"))
            try:
                await asyncio.Event().wait()
            finally:
                stopped.set()

        async def drive():
            while not pygame.display.get_init():
                await asyncio.sleep(0)
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
            for _ in range(100):
                if engine.riders[0].direction == simulator.Direction.UP:
                    if keyboard_only or engine.riders[1].direction == simulator.Direction.DOWN:
                        break
                await asyncio.sleep(0.005)
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        with patch.object(simulator, "Engine", return_value=engine), patch.object(
            simulator, "receive_controllers", side_effect=receiver
        ):
            driver = asyncio.create_task(drive())
            try:
                await asyncio.wait_for(simulator.run_game(keyboard_only), 2)
                await driver
            finally:
                driver.cancel()
                await asyncio.gather(driver, return_exceptions=True)
        self.assertEqual(engine.riders[0].direction, simulator.Direction.UP)
        self.assertFalse(pygame.get_init())
        if keyboard_only:
            self.assertFalse(receiver_started)
            self.assertEqual(engine.riders[1].direction, simulator.Direction.LEFT)
        else:
            self.assertEqual(engine.riders[1].direction, simulator.Direction.DOWN)
            self.assertTrue(stopped.is_set())

    async def test_keyboard_only(self):
        await self.play(keyboard_only=True)

    async def test_keyboard_and_ble_with_clean_shutdown(self):
        await self.play(keyboard_only=False)

    async def test_missing_ble_dependency_leaves_keyboard_available(self):
        with patch.dict("sys.modules", bleak=None):
            await simulator.receive_controllers(asyncio.Queue())
        await self.play(keyboard_only=True)


    async def test_a_and_space_round_transition_discards_old_directions(self):
        for use_space in (False, True):
            with self.subTest(use_space=use_space):
                engine = simulator.Engine()
                engine.finished = True
                engine.scores = [3, 1]
                queue = asyncio.Queue()
                for event in (("P1", "UP"), ("P1", "A"), ("P2", "A"),
                              ("P2", "DOWN")):
                    queue.put_nowait(event)
                events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if use_space else []
                with patch.object(simulator, "Engine", return_value=engine), patch.object(
                    pygame.event, "get", side_effect=[events, [pygame.event.Event(pygame.QUIT)]]
                ), patch.object(engine, "restart_match", wraps=engine.restart_match) as restart:
                    try:
                        await asyncio.wait_for(simulator.game_loop(queue), 1)
                    finally:
                        pygame.quit()
                restart.assert_called_once()
                self.assertEqual(engine.scores, [0, 0])
                self.assertEqual(engine.riders[0].direction, simulator.Direction.RIGHT)
                self.assertEqual(engine.riders[1].direction, simulator.Direction.LEFT)
                self.assertEqual(engine.riders[0].pos, (16, 32))
                await asyncio.wait_for(queue.join(), 1)
