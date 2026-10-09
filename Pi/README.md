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
