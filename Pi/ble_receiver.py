"""Receive Pico button packets and expose normalized events through a queue."""

import asyncio

from config import SETTINGS

DEVICE_NAME = SETTINGS["DEVICE_NAME"]
INPUT_UUID = SETTINGS["INPUT_UUID"]
PLAYER_ID = SETTINGS.get("PLAYER_ID", "P1")
ACK = 0xFE

COMMANDS = {
    1: "UP",
    2: "DOWN",
    3: "LEFT",
    4: "RIGHT",
}


def parse_packet(data):
    """Return (direction, Pico timestamp bytes) or raise ValueError."""
    packet = bytes(data)
    if len(packet) != 5:
        raise ValueError("expected 5 bytes, received {}".format(len(packet)))

    direction = COMMANDS.get(packet[0])
    if direction is None:
        raise ValueError("unknown command byte {}".format(packet[0]))

    return direction, packet[1:5]


def make_handler(client, input_queue, player_id=PLAYER_ID):
    """Create a Bleak notification callback that validates, queues, and ACKs."""
    async def handle_input(sender, data):
        try:
            direction, timestamp = parse_packet(data)
        except (TypeError, ValueError) as error:
            print("Ignoring malformed button packet:", error)
            return

        input_queue.put_nowait((player_id, direction))
        ack = bytes((ACK, data[0])) + timestamp
        try:
            await client.write_gatt_char(INPUT_UUID, ack, response=True)
        except Exception as error:
            print("Could not acknowledge button packet:", error)

    return handle_input


async def consume_input_queue(input_queue):
    """Standalone consumer for checking queue order without a game engine."""
    while True:
        player_id, direction = await input_queue.get()
        try:
            print("Input:", player_id, direction)
        finally:
            input_queue.task_done()


async def run_receiver(input_queue):
    # Import Bleak only when running the receiver so this module remains
    # importable for tests and other game-side consumers without BLE hardware.
    from bleak import BleakClient, BleakScanner

    while True:
        try:
            print("Searching for", DEVICE_NAME + "...")
            device = await BleakScanner.find_device_by_name(
                DEVICE_NAME, timeout=10.0
            )
            if device is None:
                print("Controller not found")
                await asyncio.sleep(2)
                continue

            async with BleakClient(device) as client:
                print("Connected to controller")
                await client.start_notify(
                    INPUT_UUID, make_handler(client, input_queue)
                )
                while client.is_connected:
                    await asyncio.sleep(0.1)
        except Exception as error:
            print("BLE error:", error)

        print("Retrying connection...")
        await asyncio.sleep(2)


async def main():
    input_queue = asyncio.Queue()
    consumer = asyncio.create_task(consume_input_queue(input_queue))
    try:
        await run_receiver(input_queue)
    finally:
        consumer.cancel()
        try:
            await consumer
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
