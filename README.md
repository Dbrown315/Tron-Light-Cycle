# Tron Light Cycles

Repository for Senior Design 2, Team 2.

**Authors:** David Brown, Justin Guthrie, Cooper Johnson, Emmanuel Nwokedi

## Project contents

- `Pico/controller/` — MicroPython button input and debounce test for a Raspberry Pi Pico or Pico W/WH.
- `Matrix/` — scripts and utilities for testing the LED matrix.

## Pico button controller

The current controller reads four buttons and counts presses until it reaches 20. It uses the Pico's internal pull-ups, so connect each button between its GPIO and GND:

| Button | GPIO |
| --- | --- |
| Up | GP0 |
| Down | GP1 |
| Left | GP2 |
| Right | GP3 |

To run it, connect the Pico over USB, open `Pico/controller/` in VS Code with the MicroPico extension, upload the project, then enter `import main` in the MicroPico terminal. MicroPython runs the files on the Pico; it does not compile them on the host. When the 20-press test completes, the script returns to the REPL. To run it again in the same REPL session, clear the module cache and import it again:

```python
import sys
del sys.modules["main"]
import main
```

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
