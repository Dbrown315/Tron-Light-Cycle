#
# File: simulator.py
# Group: Group 9
# Purpose: Implementation of player input controls for controlling game
#          characters.

import pygame

try:
    from .engine import Engine, Direction
except ImportError:
    from engine import Engine, Direction

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


def main():
    pygame.init()
    engine = Engine()
    screen = pygame.display.set_mode((engine.size * CELL, engine.size * CELL + 55))
    pygame.display.set_caption("TRON — Level 1 simulator")
    font = pygame.font.SysFont("dejavusans", 17)
    clock = pygame.time.Clock()
    running = True
    accumulator = 0
    while running:
        dt = min(clock.tick(60) / 1000, 0.1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if engine.match_winner is not None:
                        engine.restart_match()
                    else:
                        engine.next_round()
                    accumulator = 0
                elif event.key in KEYS:
                    player, direction = KEYS[event.key]
                    engine.turn(player, direction)
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
            status += "   |   SPACE: next round / new match"
        screen.blit(
            font.render(status, True, (220, 235, 245)), (8, engine.size * CELL + 14)
        )
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
