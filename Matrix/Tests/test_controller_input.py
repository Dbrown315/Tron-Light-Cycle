"""Hardware-free tests of the receiver-to-engine path."""
import asyncio
import unittest

from Game.controller_input import advance_round, drain_controller_inputs
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


class ActionInputTests(unittest.TestCase):
    def drain(self, engine, *events, **kwargs):
        queue = asyncio.Queue()
        for event in events:
            queue.put_nowait(event)
        advanced = drain_controller_inputs(engine, queue, **kwargs)
        self.assertTrue(queue.empty())
        self.assertEqual(queue._unfinished_tasks, 0)
        return advanced

    def test_either_player_can_advance_and_scores_are_preserved(self):
        for player in ("P1", "P2"):
            with self.subTest(player=player):
                engine = Engine()
                engine.finished = True
                engine.scores = [1, 2]
                engine.round_number = 4
                self.assertTrue(self.drain(engine, (player, "A")))
                self.assertFalse(engine.finished)
                self.assertEqual(engine.scores, [1, 2])
                self.assertEqual(engine.round_number, 4)

    def test_match_restart_and_duplicate_actions(self):
        engine = Engine()
        engine.finished = True
        engine.scores = [3, 2]
        engine.round_number = 6
        self.assertTrue(self.drain(engine, ("P1", "A"), ("P2", "A")))
        self.assertEqual(engine.scores, [0, 0])
        self.assertEqual(engine.round_number, 1)
        self.assertFalse(engine.finished)

    def test_actions_during_play_do_not_change_game(self):
        engine = Engine()
        engine.scores = [1, 0]
        self.assertFalse(self.drain(engine, ("P1", "A"), ("P2", "B")))
        self.assertEqual(engine.scores, [1, 0])
        self.assertEqual(engine.riders[0].direction, Direction.RIGHT)
        self.assertEqual(engine.riders[1].direction, Direction.LEFT)

    def test_b_and_unknown_player_cannot_advance(self):
        engine = Engine()
        engine.finished = True
        self.assertFalse(self.drain(engine, ("P1", "B"), ("unknown", "A")))
        self.assertTrue(engine.finished)

    def test_directions_before_and_after_a_are_stale(self):
        engine = Engine()
        engine.finished = True
        self.assertTrue(self.drain(engine, ("P1", "UP"), ("P2", "A"),
                                   ("P2", "DOWN")))
        self.assertEqual(engine.riders[0].direction, Direction.RIGHT)
        self.assertEqual(engine.riders[1].direction, Direction.LEFT)

    def test_space_then_a_cannot_advance_twice_or_apply_stale_directions(self):
        engine = Engine()
        engine.finished = True
        engine.scores = [3, 1]
        self.assertTrue(advance_round(engine))
        self.assertFalse(self.drain(engine, ("P1", "A"), ("P1", "UP"),
                                    discard_directions=True))
        self.assertFalse(advance_round(engine))
        self.assertEqual(engine.riders[0].direction, Direction.RIGHT)
        self.assertEqual(engine.scores, [0, 0])
