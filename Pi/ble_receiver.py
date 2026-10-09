
import asyncio
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "TRON-P1"
INPUT_UUID = "12345678-1234-5678-1234-56789abcdef1"
ACK = 0xFE

COMMANDS = {
    1: "UP",
    2: "DOWN",
    3: "LEFT",
    4: "RIGHT",
}


def make_handler(client):
    async def handle_input(sender, data):
        if len(data) != 5:
            print("Invalid packet length:", len(data))
            return

        direction = COMMANDS.get(data[0])

        if direction is None:
            print("Unknown command:", data[0])
            return

        print("Received:", direction)
        ack = bytes((ACK, data[0])) + bytes(data[1:5])
        await client.write_gatt_char(INPUT_UUID, ack, response=True)

    return handle_input


async def main():
    while True:
        try:
            print("Searching for TRON-P1...")

            device = await BleakScanner.find_device_by_name(
                DEVICE_NAME, timeout=10.0
            )

            if device is None:
                print("Controller not found")
                await asyncio.sleep(2)
                continue

            async with BleakClient(device) as client:
                print("Connected to controller")

                await client.start_notify(INPUT_UUID, make_handler(client))

                while client.is_connected:
                    await asyncio.sleep(0.1)

        except Exception as error:
            print("BLE error:", error)

        print("Retrying connection...")
        await asyncio.sleep(2)


asyncio.run(main())
