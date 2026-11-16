# Pico Controller

This folder contains a MicroPython BLE button controller for a Raspberry Pi Pico or Pico W/WH. MicroPython runs the Python files on the board; the code is not compiled on the host.

## Wiring

The button inputs are configured with internal pull-up resistors in `buttons.py`:

| Button | GPIO |
| --- | --- |
| Up | GP0 |
| Down | GP1 |
| Left | GP2 |
| Right | GP3 |
| A | GP22 |
| B | GP21 |

Connect each button between its GPIO pin and GND. The GPIO numbers in the code refer to GPIOs, not the Pico's physical header pin numbers. Do not connect a button input to 3V3 when using this pull-up configuration.

## Upload and run

1. Connect the Pico over USB and open this folder in VS Code.
2. Use the MicroPico extension to connect to the Pico.
3. If this folder has not been initialized before, run **MicroPico: Initialize MicroPico project**. The `.micropico` marker is in this folder.
4. Run **MicroPico: Upload project to Pico** to copy the controller files, including `config.py`, `ble_controller.py`, and `settings.env`, to the board.
5. In the MicroPico terminal, enter:

   ```python
   import main
   ```

`main.py` continuously polls the buttons. A press is reported after the input is
stable for 20 ms, while the button is still held. Debouncing does not pause the
polling loop or wait for release; holding a button produces one command, and a
new command requires a debounced release followed by another press.

Because `main` is cached after import, entering `import main` again in the same REPL session will not rerun it. To run another round without a soft reset, use:

```python
import sys
del sys.modules["main"]
import main
```

Alternatively, soft-reset the board and run `import main` again.

## Button actions

Direction buttons steer the assigned player. A advances a finished round or starts
a new match after a player reaches three wins; it does nothing during active play.
B is sent to the Pi but has no assigned game action yet. Each button produces one
command per press, including A and B.

Update the Pi receiver before using the updated firmware: A/B use new command
bytes (5 and 6) that older receivers reject. Direction-only firmware remains
compatible with the updated receiver. When uploading, preserve each Pico's
`DEVICE_NAME` (`TRON-P1` or `TRON-P2`) in its `settings.env`.

## BLE button latency

Run `main.py` on the Pico and `python3 Pi/ble_receiver.py` on the Pi. Press a
controller button; the Pico console reports estimated one-way delivery latency
and the running average based on the acknowledgment round trip. See
[Pi/README.md](../../Pi/README.md) for editing GPIO and BLE settings in
`settings.env`.
