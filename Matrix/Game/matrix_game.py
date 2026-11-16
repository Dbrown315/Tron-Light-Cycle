#
# File: matrix_game.py
# Group: Group 9
# Purpose: Connects the game engine, peripheral input, and matrix renderer.

import argparse
import time

import pygame

from .engine import Direction, Engine
from .frame_builder import build_frame
from .round_effects import result_frame

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


def run(ticks=8, colors=("blue", "orange"), simulate=False):
    # Import hardware when driving matrix
    if simulate:

        class Preview:
            def __init__(self):
                self.screen = pygame.display.set_mode((512, 512))

            def show_pixels(self, frame):
                surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                self.screen.blit(pygame.transform.scale(surf, (512, 512)), (0, 0))
                pygame.display.flip()

            def clear(self):
                self.screen.fill((0, 0, 0))
                pygame.display.flip()

            renderer = None

    else:
        from .matrix_renderer import MatrixRenderer

        renderer = MatrixRenderer()

    pygame.init()
    if simulate:
        renderer = Preview()
    else:
        pygame.display.set_mode((360, 120))
        pygame.display.set_caption("TRON matrix control | focus here for keyboard")
    clock = pygame.time.Clock()
    engine = Engine()
    running = True
    next_tick = time.monotonic() + 1 / ticks
    last_finished = False
    print("WASD: P1 | Arrows: P2 | SPACE: next round | R: restart | ESC: exit")
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in KEYS and not engine.finished:
                        player, direction = KEYS[event.key]
                        engine.turn(player, direction)
                    elif event.key == pygame.K_SPACE and engine.finished:
                        if engine.match_winner is None:
                            engine.next_round()
                        else:
                            engine.restart_match()
                        next_tick = time.monotonic() + 1 / ticks
                        last_finished = False
                        finish_time = None
                    elif event.key == pygame.K_r:
                        engine.restart_match()
                        next_tick = time.monotonic() + 1 / ticks
                        last_finished = False
                        finish_time = None
            now = time.monotonic()
            if not engine.finished and now >= next_tick:
                engine.step()
                next_tick = now + 1 / ticks
            if engine.finished and not last_finished:
                print(
                    f"Round {engine.round_number} finished. Winner: {engine.winner}; scores: {engine.scores}; match winner: {engine.match_winner}"
                )
                finish_time = time.monotonic()
                last_finished = True
            frame = build_frame(engine, colors)
            if engine.finished and finish_time is not None:
                frame = result_frame(
                    frame, 
                    engine.winner, 
                    time.monotonic() - finish_time,
                    colors=colors,
                )
            renderer.show_pixels(frame)
            clock.tick(30)
    finally:
        renderer.clear()
        pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--simulate", action="store_true", help="Preview without matrix hardware"
    )
    parser.add_argument("--ticks", type=float, default=8)
    parser.add_argument(
        "--p1",
        choices=list(__import__("Game.frame_builder", fromlist=["COLORS"]).COLORS),
        default="blue",
    )
    parser.add_argument(
        "--p2",
        choices=list(__import__("Game.frame_builder", fromlist=["COLORS"]).COLORS),
        default="orange",
    )
    args = parser.parse_args()
    if args.ticks <= 0 or args.ticks > 30:
        parser.error("--ticks must be greater than 0 and at most 30")
    if args.p1 == args.p2:
        parser.error("Players must have different colors")
    run(args.ticks, (args.p1, args.p2), args.simulate)
