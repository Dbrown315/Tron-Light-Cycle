# Raspberry Pi BLE

Run `ble_receiver.py` to receive button directions and acknowledge each press
for the Pico's latency measurement. On the Pi, install Bleak in the project's
Python environment, then run:

```bash
python3 Pi/ble_receiver.py
```

With `main.py` running on the Pico, press a button. The Pico console prints an
estimated one-way button delivery latency. The Pico measures from sending the
button notification until its acknowledgment returns, then divides that round
trip by two. This is an estimate because BLE delivery and acknowledgment times
can differ in each direction.

Edit `Pi/settings.env` and `Pico/controller/settings.env` to change the device
name or BLE UUIDs. Keep the shared BLE values identical in both files. Change
the Pico GPIO assignments in `Pico/controller/settings.env`; these are GPIO
numbers, not header pin numbers. The scripts use built-in defaults if the
settings file is missing.
