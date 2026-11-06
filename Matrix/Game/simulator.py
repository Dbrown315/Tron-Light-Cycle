#
# File: simulator.py
# Group: Group 9
# Purpose: Implementation of player input controls for controlling game
#          characters.

import argparse
import asyncio
from pathlib import Path
import sys

import pygame

# Also support direct-script launches and `python -m Game.simulator` in Matrix/.
REPO_ROOT = str(Path(__file__).resolve().parents[2])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from .engine import Engine, Direction
    from .controller_input import advance_round, drain_controller_inputs
except ImportError:
    from engine import Engine, Direction
    from controller_input import advance_round, drain_controller_inputs

CELL = 9
COLORS = ((65, 220, 255), (255, 95, 170))
KEYS = {
    pygame.K_w: (0, Direction.UP),
    pygame.K_d: (0, Direction.RIGHT),
    pygame.K_s: (0, Direction.DOWN),
    pygame.K_a: (0, Direction.LEFT),
    pygame.K_UP: (1, Direction.UP),
    pygame.K_RIGHT: (1, Direction.RIGHT),
    pygame.K_DOWN: (1, Direction.DOWN),
    pygame.K_LEFT: (1, Direction.LEFT),
}


async def receive_controllers(input_queue):
    try:
        from Pi.ble_receiver import run_receiver
        await run_receiver(input_queue)
    except Exception as error:
        print("BLE input unavailable; keyboard controls remain active:", error)


async def run_game(keyboard_only=False):
    input_queue = asyncio.Queue()
    receiver = None
    try:
        if not keyboard_only:
            receiver = asyncio.create_task(receive_controllers(input_queue))
        await game_loop(input_queue)
    finally:
        if receiver is not None:
            receiver.cancel()
            await asyncio.gather(receiver, return_exceptions=True)
        pygame.quit()


async def game_loop(input_queue):
    pygame.init()
    engine = Engine()
    screen = pygame.display.set_mode((engine.size * CELL, engine.size * CELL + 55))
    pygame.display.set_caption("TRON — Level 1 simulator")
    font = pygame.font.SysFont("dejavusans", 17)
    loop = asyncio.get_running_loop()
    previous_frame = loop.time()
    running = True
    accumulator = 0
    while running:
        frame_start = loop.time()
        dt = min(frame_start - previous_frame, 0.1)
        previous_frame = frame_start
        round_was_finished = engine.finished
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if advance_round(engine):
                        accumulator = 0
                        dt = 0
                elif event.key in KEYS:
                    player, direction = KEYS[event.key]
                    engine.turn(player, direction)
        if not running:
            break
        if drain_controller_inputs(
            engine, input_queue, discard_directions=round_was_finished
        ):
            accumulator = 0
            dt = 0
        if not engine.finished:
            accumulator += dt
            while accumulator >= 0.13 and not engine.finished:
                engine.step()
                accumulator -= 0.13
        screen.fill((5, 10, 22))
        for i, trail in enumerate(engine.trails):
            for x, y in trail:
                pygame.draw.rect(
                    screen, COLORS[i], (x * CELL, y * CELL, CELL - 1, CELL - 1)
                )
        for i, rider in enumerate(engine.riders):
            if rider.alive:
                x, y = rider.pos
                pygame.draw.rect(
                    screen, (255, 255, 255), (x * CELL, y * CELL, CELL - 1, CELL - 1)
                )
        status = f"P1 {engine.scores[0]} - {engine.scores[1]} P2 | Round {engine.round_number}"
        if engine.finished:
            status += " | A/SPACE: next round/match"
        screen.blit(
            font.render(status, True, (220, 235, 245)), (8, engine.size * CELL + 14)
        )
        pygame.display.flip()
        await asyncio.sleep(max(0, 1 / 60 - (loop.time() - frame_start)))


def main():
    parser = argparse.ArgumentParser(description="TRON keyboard and BLE simulator")
    parser.add_argument("--keyboard-only", action="store_true",
                        help="disable Bluetooth discovery")
    args = parser.parse_args()
    try:
        asyncio.run(run_game(keyboard_only=args.keyboard_only))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
