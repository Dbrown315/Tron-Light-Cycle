"""Receive Pico button packets and expose normalized events through a queue."""

import asyncio

if __package__:
    from .config import SETTINGS
else:
    from config import SETTINGS

INPUT_UUID = SETTINGS["INPUT_UUID"]

CONTROLLERS = {
    SETTINGS["DEVICE_NAME_P1"]: "P1",
    SETTINGS["DEVICE_NAME_P2"]: "P2",
}

ACK = 0xFE

COMMANDS = {
    1: "UP",
    2: "DOWN",
    3: "LEFT",
    4: "RIGHT",
    5: "A",
    6: "B",
}


def parse_packet(data):
    """Return (button, Pico timestamp bytes) or raise ValueError."""
    packet = bytes(data)
    if len(packet) != 5:
        raise ValueError("expected 5 bytes, received {}".format(len(packet)))

    button = COMMANDS.get(packet[0])
    if button is None:
        raise ValueError("unknown command byte {}".format(packet[0]))

    return button, packet[1:5]


def make_handler(client, input_queue, player_id="P1"):
    """Create a Bleak notification callback that validates, queues, and ACKs."""
    async def handle_input(sender, data):
        try:
            button, timestamp = parse_packet(data)
        except (TypeError, ValueError) as error:
            print("Ignoring malformed button packet:", error)
            return

        input_queue.put_nowait((player_id, button))
        ack = bytes((ACK, data[0])) + timestamp
        try:
            await client.write_gatt_char(INPUT_UUID, ack, response=True)
        except Exception as error:
            print("Could not acknowledge button packet:", error)

    return handle_input


async def consume_input_queue(input_queue):
    """Standalone consumer for checking queue order without a game engine."""
    while True:
        player_id, button = await input_queue.get()
        try:
            print("Input:", player_id, button)
        finally:
            input_queue.task_done()


async def run_receiver(input_queue):
    # Import Bleak only when running the receiver so this module remains
    # importable for tests and other game-side consumers without BLE hardware.
    from bleak import BleakClient, BleakScanner

    connection_tasks = {}

    async def connect_controller(device, player_id):
        task = asyncio.current_task()
        try:
            async with BleakClient(device) as client:
                print("Connected", player_id, "to", device.name)
                await client.start_notify(
                    INPUT_UUID,
                    make_handler(client, input_queue, player_id=player_id),
                )
                while client.is_connected:
                    await asyncio.sleep(0.1)
        except Exception as error:
            print("BLE error for", player_id, ":", error)
        finally:
            if connection_tasks.get(player_id) is task:
                del connection_tasks[player_id]
            print("Disconnected", player_id, "retrying discovery...")

    def on_device_detected(device, advertisement_data):
        device_name = advertisement_data.local_name or device.name
        player_id = CONTROLLERS.get(device_name)
        if player_id is None or player_id in connection_tasks:
            return

        print("Found", player_id, "controller", device_name)
        connection_tasks[player_id] = asyncio.create_task(
            connect_controller(device, player_id)
        )

    try:
        while True:
            try:
                print("Scanning for controllers:", ", ".join(CONTROLLERS))
                async with BleakScanner(detection_callback=on_device_detected):
                    while True:
                        await asyncio.sleep(1)
            except Exception as error:
                print("BLE scanner error:", error)
                await asyncio.sleep(2)
    finally:
        # Stop all connection tasks when the scanner is stopped or an error occurs.
        tasks = list(connection_tasks.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


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
