import asyncio
import unittest

from ble_receiver import ACK, make_handler


class FakeBleClient:
    def __init__(self):
        self.writes = []

    async def write_gatt_char(self, uuid, data, response):
        self.writes.append((uuid, bytes(data), response))


class BleReceiverTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.queue = asyncio.Queue()
        self.client = FakeBleClient()
        self.handler = make_handler(self.client, self.queue, player_id="test-player")

    async def assert_rejected(self, packet):
        await self.handler(None, packet)
        self.assertTrue(self.queue.empty())
        self.assertEqual(self.client.writes, [])

    async def test_empty_packet_is_rejected(self):
        await self.assert_rejected(b"")

    async def test_truncated_packet_is_rejected(self):
        await self.assert_rejected(b"\x01\x02")

    async def test_oversized_packet_is_rejected(self):
        await self.assert_rejected(b"\x01\x00\x00\x00\x00\x99")

    async def test_unknown_command_is_rejected(self):
        await self.assert_rejected(b"\x99\x00\x00\x00\x00")

    async def test_valid_commands_are_queued_in_order_and_acknowledged(self):
        expected = ["UP", "DOWN", "LEFT", "RIGHT"]
        for command, direction in enumerate(expected, start=1):
            packet = bytes((command, command, 0, 0, 0))
            await self.handler(None, packet)

        queued = [self.queue.get_nowait() for _ in expected]
        self.assertEqual(
            queued,
            [("test-player", direction) for direction in expected],
        )
        self.assertEqual(len(self.client.writes), 4)
        for command, (_, ack, response) in enumerate(self.client.writes, start=1):
            self.assertEqual(ack, bytes((ACK, command, command, 0, 0, 0)))
            self.assertTrue(response)

    async def test_valid_packet_still_works_after_malformed_packets(self):
        for packet in (b"", b"\x01", b"\x01\x00\x00\x00\x00\xff", b"\xff\x00\x00\x00\x00"):
            await self.handler(None, packet)

        await self.handler(None, b"\x03\x01\x00\x00\x00")
        self.assertEqual(self.queue.get_nowait(), ("test-player", "LEFT"))
        self.assertEqual(self.client.writes[0][1], bytes((ACK, 3, 1, 0, 0, 0)))


if __name__ == "__main__":
    unittest.main()
