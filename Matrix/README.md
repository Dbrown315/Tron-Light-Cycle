# Tron Light Cycles (Game Engine Prototype) - Part 2

Repository for Senior Design 2, Team 9.

## Project Contents
- `Matrix/Game` - Game engine setup, simulation of game play design and 
                  matrix rendering.
- `Matrix/Tests` - Unit test cases for testing collision logic and game logic.

From the repository root (virtual environment):

```bash
source ~/venvs/tron_venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m Matrix.Game.simulator
```

The simulator automatically scans for both BLE controllers while remaining
playable with the keyboard. `TRON-P1` controls Player 1 and `TRON-P2` controls
Player 2; these advertised names are configured in `Pi/settings.env` and each
Pico's `settings.env`. One controller is enough to play against a keyboard player.
Do not run `Pi/ble_receiver.py` separately while playing: the simulator runs its
own receiver and needs to connect to the controllers itself.

Controls: Player 1 (W/A/S/D); Player 2 (arrow keys);
Space (next round/new match); ESC (quit).
BLE direction buttons use the same turn rules as keyboard directions. Both
sources remain active; keyboard events are processed first, followed by queued
controller commands in arrival order each frame. Commands received between
rounds are discarded. Space still advances rounds; A/B buttons and GUI navigation
are not part of this integration.

For keyboard-only testing, disable BLE discovery:

```bash
python3 -m Matrix.Game.simulator --keyboard-only
```

Missing Bleak leaves keyboard play available. Bluetooth discovery errors are
printed and retried; disconnected controllers are rediscovered automatically
without pausing the game. See [Pi BLE setup](../Pi/README.md) if no controller
connects. Connection and disconnection messages appear in the launch terminal.
The simulator opens a Pygame window; run it from the Pi desktop. This command
does not render gameplay on the RGB matrix.

For the independent matrix hardware pattern:

```bash
python3 -m Matrix.Game.matrix_test
```

Rules:
- No reverse turns
- Simultaneous cell movement
- Wall/Trail/Head-on collisions
- First to three wins
- Draws score zero.
- Round counter counts attempted rounds and can exceed five after draws.


