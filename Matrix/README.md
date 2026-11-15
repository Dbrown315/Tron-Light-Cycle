# Tron Light Cycles (Game Engine) - Part 2

Repository for Senior Design 2, Team 9.

## Project Contents
- `Matrix/Game` - Game engine setup, simulation of game play design and matrix rendering.
- `Matrix/Tests` - Unit test cases for testing collision logic and game logic.

From the repository root (virtual environment):

```bash
source ~/venvs/tron_venv/bin/activate
python3 -m unittest discover -s Tests -v
python3 -m Game.simulator
python3 -m Game.matrix_test
python3 -m unittest discover -s Tests -v
python3 -m Game.matrix_game --simulate
python3 -m Game.matrix_game --ticks 8 --p1 blue --p2 orange
python3 -m unittest discover -s Tests -v
python3 GUI/display.py --simulate
python3 GUI/display.py --ticks 8
python3 -m unittest discover -s Tests -v
python3 GUI/display.py --simulate --display 1
python3 GUI/display.py --simulate --display 1 --ble
```

Controls: Player 1 (W/A/S/D); Player 2(arrow keys);
Space (next round/new match); ESC (quit).

Rules:
- No reverse turns
- Simultaneous cell movement
- Wall/Trail/Head-on collisions
- First to three wins
- Draws score zero.
- Round counter counts attempted rounds and can exceed five after draws.


