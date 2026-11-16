# Tron Light Cycles

Repository for Senior Design 2, Team 9.

**Authors:** David Brown, Justin Guthrie, Cooper Johnson, Emmanuel Nwokedi

## Project contents

- `Pico/controller/` — MicroPython button input and debounce test for a Raspberry Pi Pico or Pico W/WH.
- `Matrix/` — scripts and utilities for testing the LED matrix.

## Pico button controller

The controller continuously reads six active-low buttons and sends debounced
presses over BLE. Connect each button between its GPIO and GND:

| Button | GPIO |
| --- | --- |
| Up | GP0 |
| Down | GP1 |
| Left | GP2 |
| Right | GP3 |
| A | GP22 |
| B | GP21 |

Use the MicroPico extension to upload `Pico/controller/` to each Pico, preserving
its `DEVICE_NAME` (`TRON-P1` or `TRON-P2`) in `settings.env`, then start `main.py`.
Direction buttons steer the assigned player in the simulator. A advances a
finished round or restarts a completed match; B is currently unassigned.

See [Pico/controller/README.md](Pico/controller/README.md) for full setup and wiring instructions.

## LED matrix

The `Matrix/` directory contains two Raspberry Pi 5 test programs for a single HUB75 RGB matrix panel, configured as 64×32 with the Adafruit Matrix Bonnet pinout:

- `color_test.py` draws a rectangle, circle, and triangle, then waits for Enter before exiting.
- `label_test.py` displays the text “Hello Clemson.” and keeps the display active until interrupted with Ctrl+C.

These programs use the Raspberry Pi 5 PIO Matrix library along with NumPy and Pillow. `virtual.sh` creates `~/venvs/tron_venv` and installs the Python dependencies. From the repository root, set up and run a test with:

```bash
bash Matrix/virtual.sh
cd Matrix
source ~/venvs/tron_venv/bin/activate
python3 color_test.py
```

Run `python3 label_test.py` instead to try the text display. The matrix must be connected to the Raspberry Pi 5 using the supported pinout. The setup script also describes a udev rule needed for PIO access; follow its instructions if the program reports a permissions error. `config.sh` updates Raspberry Pi OS packages and firmware and reboots the Pi, so it is a system maintenance script rather than part of normal test startup.
