
import bluetooth
import time
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_WRITE = const(0x0008)
_ACK = const(0xFE)

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
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_WRITE,
)

service = (
    SERVICE_UUID,
    (input_characteristic,),
)

((input_handle,),) = ble.gatts_register_services(
    (service,)
)

connections = set()
latency_count = 0
latency_total_ms = 0


def advertise():
    name = b"TRON-P1"
    payload = bytes((len(name) + 1, 0x09)) + name
    ble.gap_advertise(100_000, adv_data=payload)
    print("Advertising TRON-P1")


def irq(event, data):
    global latency_count, latency_total_ms
    if event == _IRQ_CENTRAL_CONNECT:
        conn_handle, _, _ = data
        connections.add(conn_handle)
        print("Pi connected")

    elif event == _IRQ_CENTRAL_DISCONNECT:
        conn_handle, _, _ = data
        connections.discard(conn_handle)
        print("Pi disconnected")
        advertise()

    elif event == _IRQ_GATTS_WRITE:
        conn_handle, value_handle = data
        if value_handle == input_handle:
            payload = ble.gatts_read(input_handle)
            if len(payload) == 6 and payload[0] == _ACK:
                sent_ms = int.from_bytes(payload[2:6], "little")
                round_trip_ms = time.ticks_diff(time.ticks_ms(), sent_ms)
                latency_ms = round_trip_ms / 2
                latency_count += 1
                latency_total_ms += latency_ms
                print("Button delivery latency (estimated): {:.1f} ms; average over {} presses: {:.1f} ms".format(
                    latency_ms, latency_count, latency_total_ms / latency_count
                ))


ble.irq(irq)
advertise()


def send_direction(direction):
    command = COMMANDS.get(direction)
    if command is None:
        return

    sent_ms = time.ticks_ms()
    payload = bytes((command,)) + sent_ms.to_bytes(4, "little")
    ble.gatts_write(input_handle, payload)

    for conn_handle in tuple(connections):
        ble.gatts_notify(
            conn_handle, input_handle, payload
        )

    print("Sent:", direction)
