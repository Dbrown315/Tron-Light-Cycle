import asyncio
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from Pi.ble_receiver import CONTROLLERS, run_receiver


class ReceiverLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_two_players_duplicate_discovery_reconnect_and_cleanup(self):
        clients = []
        ready = asyncio.Queue()
        callback = None

        class Client:
            def __init__(self, device):
                self.device = device
                self.is_connected = True
                self.closed = False
                clients.append(self)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                self.closed = True

            async def start_notify(self, uuid, handler):
                ready.put_nowait(self)

        class Scanner:
            def __init__(self, detection_callback):
                nonlocal callback
                callback = detection_callback

            async def __aenter__(self):
                for name in CONTROLLERS:
                    device = SimpleNamespace(name=name)
                    advertisement = SimpleNamespace(local_name=name)
                    callback(device, advertisement)
                    callback(device, advertisement)
                return self

            async def __aexit__(self, *args):
                pass

        with patch.dict('sys.modules', bleak=SimpleNamespace(
            BleakClient=Client, BleakScanner=Scanner
        )):
            receiver = asyncio.create_task(run_receiver(asyncio.Queue()))
            try:
                first = await asyncio.wait_for(ready.get(), 1)
                await asyncio.wait_for(ready.get(), 1)
                self.assertEqual(len(clients), 2)
                first.is_connected = False
                async def wait_closed():
                    while not first.closed:
                        await asyncio.sleep(0.01)
                await asyncio.wait_for(wait_closed(), 1)
                callback(first.device, SimpleNamespace(local_name=first.device.name))
                await asyncio.wait_for(ready.get(), 1)
                self.assertEqual(len(clients), 3)
            finally:
                receiver.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await receiver
            self.assertTrue(all(client.closed for client in clients))
