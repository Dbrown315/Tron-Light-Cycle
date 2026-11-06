"""Hardware-free tests of the receiver-to-engine path."""
import asyncio
import unittest

from Game.controller_input import drain_controller_inputs
from Game.engine import Direction, Engine
from Pi.ble_receiver import ACK, make_handler


class ControllerInputTests(unittest.IsolatedAsyncioTestCase):
    async def test_each_button_reaches_only_its_player_and_is_acknowledged(self):
        class Client:
            async def write_gatt_char(self, uuid, data, response):
                self.ack = bytes(data)

        for player, index in (("P1", 0), ("P2", 1)):
            for command, direction in enumerate(
                (Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT), 1
            ):
                with self.subTest(player=player, direction=direction):
                    engine = Engine()
                    # Choose a perpendicular initial direction for a legal turn.
                    engine.riders[index].direction = (
                        Direction.RIGHT if command <= 2 else Direction.UP
                    )
                    other = engine.riders[1 - index].direction
                    queue = asyncio.Queue()
                    client = Client()
                    packet = bytes((command, 1, 2, 3, 4))
                    await make_handler(client, queue, player)(None, packet)
                    drain_controller_inputs(engine, queue)
                    self.assertEqual(engine.riders[index].direction, direction)
                    self.assertEqual(engine.riders[1 - index].direction, other)
                    self.assertEqual(client.ack, bytes((ACK,)) + packet)
                    await asyncio.wait_for(queue.join(), 1)

    async def test_order_reverse_rejection_and_invalid_events(self):
        engine = Engine()
        queue = asyncio.Queue()
        for event in (("P1", "LEFT"), ("P3", "UP"), ("P1", "BAD"),
                      None, ([], {}), ("P1", "UP"), ("P1", "LEFT")):
            queue.put_nowait(event)
        drain_controller_inputs(engine, queue)
        self.assertEqual(engine.riders[0].direction, Direction.LEFT)
        self.assertEqual(engine.riders[1].direction, Direction.LEFT)
        await asyncio.wait_for(queue.join(), 1)

    async def test_reverse_and_round_over_commands_are_discarded(self):
        engine = Engine()
        queue = asyncio.Queue()
        queue.put_nowait(("P1", "LEFT"))
        drain_controller_inputs(engine, queue)
        self.assertEqual(engine.riders[0].direction, Direction.RIGHT)
        engine.finished = True
        queue.put_nowait(("P1", "UP"))
        drain_controller_inputs(engine, queue)
        engine.next_round()
        drain_controller_inputs(engine, queue)
        self.assertEqual(engine.riders[0].direction, Direction.RIGHT)
        self.assertTrue(queue.empty())
