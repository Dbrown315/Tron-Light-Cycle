
import bluetooth
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)

SERVICE_UUID = bluetooth.UUID(
    "12345678-1234-5678-1234-56789abcdef0"
)
INPUT_UUID = bluetooth.UUID(
    "12345678-1234-5678-1234-56789abcdef1"
)

COMMANDS = {
    "UP": 1,
    "DOWN": 2,
    "LEFT": 3,
    "RIGHT": 4,
}

ble = bluetooth.BLE()
ble.active(True)

input_characteristic = (
    INPUT_UUID,
    _FLAG_READ | _FLAG_NOTIFY,
)

service = (
    SERVICE_UUID,
    (input_characteristic,),
)

((input_handle,),) = ble.gatts_register_services(
    (service,)
)

connections = set()


def advertise():
    name = b"TRON-P1"
    payload = bytes((len(name) + 1, 0x09)) + name
    ble.gap_advertise(100_000, adv_data=payload)
    print("Advertising TRON-P1")


def irq(event, data):
    if event == _IRQ_CENTRAL_CONNECT:
        conn_handle, _, _ = data
        connections.add(conn_handle)
        print("Pi connected")

    elif event == _IRQ_CENTRAL_DISCONNECT:
        conn_handle, _, _ = data
        connections.discard(conn_handle)
        print("Pi disconnected")
        advertise()


ble.irq(irq)
advertise()


def send_direction(direction):
    command = COMMANDS.get(direction)
    if command is None:
        return

    payload = bytes((command,))
    ble.gatts_write(input_handle, payload)

    for conn_handle in tuple(connections):
        ble.gatts_notify(
            conn_handle, input_handle, payload
        )

    print("Sent:", direction)
