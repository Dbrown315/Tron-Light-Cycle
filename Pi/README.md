# Raspberry Pi BLE

## Check Bluetooth LE on the Pi

The Pi's Bluetooth adapter must be powered on before the receiver can find the
Pico controllers. Check the adapter and whether Bluetooth is blocked:

```bash
bluetoothctl show
rfkill list bluetooth
```

In `bluetoothctl show`, confirm that an adapter is listed and `Powered: yes` is
shown. In the `rfkill` output, confirm Bluetooth is not blocked. If it is
blocked or powered off, run:

```bash
sudo rfkill unblock bluetooth
sudo systemctl enable --now bluetooth
bluetoothctl power on
bluetoothctl show
```

If `bluetoothctl show` reports no controller, check that Bluetooth is enabled
in Raspberry Pi OS and that the Pi has rebooted after any configuration change.
The receiver needs the BlueZ Bluetooth service and a working adapter.

## Run the receiver

Run `ble_receiver.py` to receive button directions, expose each command on an
`asyncio.Queue` as `(player_id, direction)`, and acknowledge each press for the
Pico's latency measurement. Its standalone consumer prints queued commands in
arrival order without requiring the game engine. On the Pi, activate the
project's Python environment, then install dependencies and run from the
repository root:

```bash
python3 -m pip install -r requirements.txt
python3 Pi/ble_receiver.py
```

With `main.py` running on the Pico, press a button. The Pico console prints an
estimated one-way button delivery latency. The Pico measures from sending the
button notification until its acknowledgment returns, then divides that round
trip by two. This is an estimate because BLE delivery and acknowledgment times
can differ in each direction.

The receiver validates five-byte packets: one command byte (`1` up, `2` down,
`3` left, `4` right), followed by the Pico timestamp in four little-endian
bytes. Invalid packets are ignored.

Edit `Pi/settings.env` and `Pico/controller/settings.env` to change the device
name or BLE UUIDs. Keep the shared BLE values identical in both files. Change
the Pico GPIO assignments in `Pico/controller/settings.env`; these are GPIO
numbers, not header pin numbers. The scripts use built-in defaults if the
settings file is missing.

## Play the simulator with controllers

The simulator consumes this receiver's queue directly; do not start a separate
receiver process while playing. From the repository root, run:

```bash
python3 -m Matrix.Game.simulator
```

Both controllers and keyboard inputs are accepted together. Player assignment is
by advertised name (`TRON-P1` / `TRON-P2`), not hardware ID. Configure a different
name in each Pico's `settings.env`. The receiver automatically retries discovery
and reconnects controllers. See the [simulator instructions](../Matrix/README.md)
for setup, controls, and keyboard-only startup.
