# Tron Light Cycle GUI Prototype

Pygame player configuration and score prototype for the Raspberry Pi 5 and
1024×600 HDMI display.

## Run

From the repository root, activate the project environment and install dependencies:

```bash
source ~/venvs/tron_venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m GUI.display
```

Run from the Pi desktop. BLE discovery starts automatically for `TRON-P1` and
`TRON-P2`, using the existing controller firmware and `Pi/settings.env` mapping.
Do not run the standalone BLE receiver or game simulator at the same time;
the GUI owns its BLE connections. Controllers reconnect automatically, and
mouse/keyboard operation remains available when Bluetooth is unavailable.

For mouse/keyboard operation without Bluetooth discovery:

```bash
python3 -m GUI.display --keyboard-only
```

Direct execution of `GUI/display.py` is also supported. Settings are saved in
`config/players.json` relative to the launch directory; launch from the repository
root to keep a consistent location.

## Controls

Each player has an independent highlight: cyan for P1, pink for P2. Both start
on their own character `−` button.

- Left/Right moves between buttons in the selected row.
- Up/Down moves between character `−/+`, color `−/+`, and shared controls.
- A activates the highlighted button. B is currently unassigned.
- Movement stops at row boundaries. Moving between rows retains the column where
  possible; the shared row contains Start, Play Again, Restart, and Exit.

Each controller can change only its own character/color settings. Both can use
the shared controls. Restart resets both player configurations and controller
highlights. Shared controls preserve their existing prototype behavior:
Start saves settings, Play Again resets scores, and Exit closes the GUI.

Mouse clicks remain available on all buttons without moving controller focus.
Name editing requires clicking **EDIT NAME** and typing with a keyboard; Enter
finishes and Escape stops editing. The temporary **P1 WINS ROUND** and
**P2 WINS ROUND** buttons remain mouse-only score simulation controls.

## Current limitations

- Start saves settings; it does not launch the game or update simulator colors.
- Ready/un-ready controls are not implemented yet.
- Character choices use text labels rather than sprites.
- Scores are simulated and are not connected to the game engine.
- No persistent leaderboard is implemented yet.
