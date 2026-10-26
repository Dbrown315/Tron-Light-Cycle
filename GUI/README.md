# Tron Light Cycle GUI Prototype - Part 1

A first-stage Pygame GUI prototype for Raspberry Pi 5 and the 52Pi EP-0170 7-inch HDMI display.

## Project Scope

This prototype includes:
- two player name fields (click **EDIT NAME**, type, press Enter)
- seven character choices, changed with `−` and `+`
- eight trail colors, changed with `−` and `+`
- two-player match scoreboard
- Start, Play Again, Restart, and Exit
- temporary **P1 WINS ROUND** / **P2 WINS ROUND** buttons for testing scoreboard behavior
- saves player settings to `config/players.json` when Start is selected

The round-win buttons are test controls, not game logic.

## Display note

The 52Pi EP-0170 is a 1024×600 HDMI monitor and does not have a touch panel according to its product documentation. Use a keyboard/mouse for this display.

## Run on Raspberry Pi OS

Install the `pygame` package inside a virtual environment:

```bash
source ~/venvs/tron_venv/bin/activate
python3 -m pip install pygame
python3 -c "import pygame; print(pygame.version.ver)"
```

From the project root, run:

```bash
python3 -m pygame.examples.aliens
```

If the demo opens and closes normally, Pygame is working. Then run this prototype from its folder:

```bash
python3 display.py
```

## Keyboard

- Click **EDIT NAME**, type a name, press Enter to finish.
- Escape cancels name editing.
- Use mouse clicks on the controls.
- Close the window or click **EXIT** to quit.

## Current Limitations

- The GUI is not connected to the game engine or BLE controllers.
- Character icons are represented by text labels; pixel-art sprites can be added in a later iteration.
- Score buttons simulate round outcomes for testing.
- No persistent leaderboard is implemented yet.
