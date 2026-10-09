# Pico Controller

This folder contains a MicroPython button test for a Raspberry Pi Pico or Pico W/WH. MicroPython runs the Python files on the board; the code is not compiled on the host.

## Wiring

The button inputs are configured with internal pull-up resistors in `buttons.py`:

| Button | GPIO |
| --- | --- |
| Up | GP0 |
| Down | GP1 |
| Left | GP2 |
| Right | GP3 |

Connect each button between its GPIO pin and GND. The GPIO numbers in the code refer to GPIOs, not the Pico's physical header pin numbers. Do not connect a button input to 3V3 when using this pull-up configuration.

## Upload and run

1. Connect the Pico over USB and open this folder in VS Code.
2. Use the MicroPico extension to connect to the Pico.
3. If this folder has not been initialized before, run **MicroPico: Initialize MicroPico project**. The `.micropico` marker is in this folder.
4. Run **MicroPico: Upload project to Pico** to copy `main.py` and `buttons.py` to the board.
5. In the MicroPico terminal, enter:

   ```python
   import main
   ```

`main.py` counts recognized button presses until it reaches 20, then prints the totals and returns to the REPL. Pressing a button is recognized after it has remained down for the debounce interval; the code waits for release before reporting it.

Because `main` is cached after import, entering `import main` again in the same REPL session will not rerun it. To run another round without a soft reset, use:

```python
import sys
del sys.modules["main"]
import main
```

Alternatively, soft-reset the board and run `import main` again.

## BLE button latency

Run `main.py` on the Pico and `python3 Pi/ble_receiver.py` on the Pi. Press a
controller button; the Pico console reports estimated one-way delivery latency
and the running average based on the acknowledgment round trip. See
[Pi/README.md](../../Pi/README.md).
