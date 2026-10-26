#
# File: display.py
# Group: Group 9
# Purpose: Create the Graphical User Interface for user interactions and game
#          settings using the Pygame Library.

""" """

import json
import os
import sys
from pathlib import Path

import pygame

WIDTH, HEIGHT = 1024, 600
FPS = 30
CONFIG_PATH = Path("config") / "players.json"

BG = (5, 10, 22)
PANEL = (12, 22, 42)
PANEL_ALT = (9, 17, 33)
CYAN = (54, 225, 255)
PINK = (255, 78, 151)
WHITE = (238, 246, 255)
MUTED = (139, 165, 190)
BORDER = (35, 76, 105)
GREEN = (93, 255, 183)
AMBER = (255, 205, 89)

# Game Characters
CHARACTERS = ["Spider", "Dino", "Ladybird", "Tiger", "Dragonfly", "Ant", "Butterfly"]

# Game Colors: white (default)
COLORS = {
    "red": (255, 75, 85),
    "orange": (255, 151, 64),
    "yellow": (255, 224, 88),
    "green": (92, 242, 139),
    "blue": (63, 191, 255),
    "indigo": (106, 103, 255),
    "violet": (197, 111, 255),
    "white": (238, 246, 255),
}


# Rectangular Padding
def inset(rect, dx, dy):
    """
    Return a smaller rectangle with internal padding
    """
    return pygame.Rect(rect.x + dx, rect.y + dy, rect.w - 2 * dx, rect.h - 2 * dx)


# Equal-width columns
def columns(rect, count, gap=12):
    """
    Divide a rectangle into equally sized columns.
    """
    width = (rect.w - gap * (count - 1)) // count

    return [
        pygame.Rect(rect.x + i * (width + gap), rect.y, width, rect.h)
        for i in range(count)
    ]


# Text-fitting and alignment
def draw_fitted_text(surface, content, font, color, rect, align="left"):
    """
    Draw text inside a bounded rectangle
    """

    rect = pygame.Rect(rect)
    rendered = font.render(str(content), True, color)

    if rendered.get_width() > rect.width:
        scale = rect.width / rendered.get_with()
        new_size = max(9, int(font.get_height() * scale))

        fitted_font = pygame.font.SysFont("dejavusans", new_size, bold=font.get_bold())

        rendered = fitted_font.render(str(content), True, color)

        destination = rendered.get_rect()

        if align == "center":
            destination.center = rect.center
        elif align == "right":
            destination.midright = rect.midright
        else:
            destination.midleft = rect.midleft

        old_clip = surface.get_clip()
        surface.set_clip(rect)
        surface.blit(rendered, destination)
        surface.set_clip(old_clip)


DEFAULT_PLAYERS = [
    {"name": "Player A", "character": "spider", "color": "white"},
    {"name": "Player B", "character": "dino", "color": "blue"},
]


def load_players():
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list) and len(data) == 2:
            players = []
            for i, p in enumerate(data):
                players.append(
                    {
                        "name": str(p.get("name", f"Player {i+1}"))[:16],
                        "character": (
                            p.get("character")
                            if p.get("character") in CHARACTERS
                            else CHARACTERS[i]
                        ),
                        "color": (
                            p.get("color") if p.get("color") in COLORS else "white"
                        ),
                    }
                )
            return players
    except (OSError, ValueError, TypeError):
        pass
    return [p.copy() for p in DEFAULT_PLAYERS]


def save_players(players):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(players, indent=2), encoding="utf-8")


class Button:
    def __init__(self, rect, label, action, accent=CYAN, fill=PANEL_ALT, font_size=18):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action
        self.accent = accent
        self.fill = fill
        self.font_size = font_size

    def draw(self, surface, font):
        pygame.draw.rect(surface, self.fill, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.accent, self.rect, width=2, border_radius=8)
        f = pygame.font.SysFont("dejavusans", self.font_size, bold=True)
        text = f.render(self.label, True, WHITE)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


def main():
    pygame.init()
    pygame.display.set_caption("TRON // Light Cycle Arena - GUI Prototype")
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("dejavusans", 30, bold=True)
    name_font = pygame.font.SysFont("dejavusans", 23, bold=True)
    sub_font = pygame.font.SysFont("dejavusans", 13, bold=True)
    font = pygame.font.SysFont("dejavusans", 17)
    small_font = pygame.font.SysFont("dejavusans", 13)

    players = load_players()
    scores = [0, 0]
    round_number = 1
    active_name = None
    status = "Configure both riders, then select START."
    running = True
    buttons = []
    target_surface = screen

    def add_text(text, pos, color=WHITE, f=font, anchor="topleft"):
        image = f.render(text, True, color)
        rect = image.get_rect()
        setattr(rect, anchor, pos)
        target_surface.blit(image, rect)

    def build_buttons():
        result = []
        # Player config controls
        for i, x in enumerate((36, 522)):
            accent = CYAN if i == 0 else PINK
            result.append(
                Button(
                    (x + 18, 238, 38, 34), "−", ("char_prev", i), accent, font_size=20
                )
            )
            result.append(
                Button(
                    (x + 65, 238, 38, 34), "+", ("char_next", i), accent, font_size=20
                )
            )
            result.append(
                Button(
                    (x + 18, 294, 38, 34), "−", ("color_prev", i), accent, font_size=20
                )
            )
            result.append(
                Button(
                    (x + 65, 294, 38, 34), "+", ("color_next", i), accent, font_size=20
                )
            )
        result.extend(
            [
                Button((36, 474, 150, 48), "START", ("start",), CYAN, (7, 54, 72), 17),
                Button(
                    (196, 474, 150, 48),
                    "PLAY AGAIN",
                    ("play_again",),
                    GREEN,
                    PANEL_ALT,
                    15,
                ),
                Button(
                    (356, 474, 150, 48), "RESTART", ("restart",), AMBER, PANEL_ALT, 17
                ),
                Button(
                    (516, 474, 150, 48),
                    "P1 WINS ROUND",
                    ("score", 0),
                    CYAN,
                    PANEL_ALT,
                    13,
                ),
                Button(
                    (676, 474, 150, 48),
                    "P2 WINS ROUND",
                    ("score", 1),
                    PINK,
                    PANEL_ALT,
                    13,
                ),
                Button((836, 474, 150, 48), "EXIT", ("exit",), PINK, (54, 17, 37), 17),
                Button(
                    (36, 180, 110, 32),
                    "EDIT NAME",
                    ("edit_name", 0),
                    CYAN,
                    PANEL_ALT,
                    12,
                ),
                Button(
                    (522, 180, 110, 32),
                    "EDIT NAME",
                    ("edit_name", 1),
                    PINK,
                    PANEL_ALT,
                    12,
                ),
            ]
        )
        return result

    while running:
        sw, sh = screen.get_size()
        # Window size: 1024x600
        canvas = pygame.Surface((WIDTH, HEIGHT))
        target_surface = canvas
        canvas.fill(BG)

        # Subtle grid
        for gx in range(0, WIDTH, 32):
            pygame.draw.line(canvas, (10, 27, 45), (gx, 0), (gx, HEIGHT), 1)
        for gy in range(0, HEIGHT, 32):
            pygame.draw.line(canvas, (10, 27, 45), (0, gy), (WIDTH, gy), 1)

        pygame.draw.rect(canvas, PANEL, (24, 20, 976, 82), border_radius=12)
        pygame.draw.rect(canvas, CYAN, (24, 20, 976, 82), 2, border_radius=12)
        add_text("TRON", (44, 29), CYAN, title_font)
        add_text("LIGHT CYCLE  //  ARENA CONTROL", (47, 68), MUTED, sub_font)
        add_text("GUI PROTOTYPE  •  LEVEL 1", (978, 45), WHITE, sub_font, "topright")

        # Player cards
        for i, x in enumerate((24, 510)):
            accent = CYAN if i == 0 else PINK
            p = players[i]
            pygame.draw.rect(canvas, PANEL, (x, 118, 478, 224), border_radius=12)
            pygame.draw.rect(canvas, accent, (x, 118, 478, 224), 2, border_radius=12)
            add_text(f"PLAYER {i+1}", (x + 18, 132), accent, sub_font)
            name_rect = pygame.Rect(x + 18, 151, 280, 28)
            add_text(p["name"], name_rect.topleft, WHITE, name_font)
            add_text("CHARACTER", (x + 18, 222), MUTED, small_font)
            add_text(p["character"].upper(), (x + 145, 243), WHITE, font)
            add_text("COLOR TRAIL", (x + 18, 278), MUTED, small_font)
            add_text(p["color"].upper(), (x + 145, 299), COLORS[p["color"]], font)
            pygame.draw.circle(canvas, COLORS[p["color"]], (x + 424, 282), 12)
            pygame.draw.circle(canvas, WHITE, (x + 424, 282), 12, 1)
            add_text(
                "Click EDIT NAME to change player name",
                (x + 18, 316),
                MUTED,
                small_font,
            )

        # Scoreboard
        pygame.draw.rect(canvas, PANEL, (24, 356, 976, 98), border_radius=12)
        pygame.draw.rect(canvas, BORDER, (24, 356, 976, 98), 2, border_radius=12)
        add_text("MATCH SCORE", (42, 367), MUTED, sub_font)
        add_text(players[0]["name"], (42, 391), COLORS[players[0]["color"]], font)
        add_text(str(scores[0]), (340, 383), COLORS[players[0]["color"]], title_font)
        add_text("—", (485, 389), MUTED, title_font)
        add_text(str(scores[1]), (600, 383), COLORS[players[1]["color"]], title_font)
        add_text(players[1]["name"], (660, 391), COLORS[players[1]["color"]], font)
        add_text(
            f"ROUND {min(round_number, 5)} / 5", (976, 373), WHITE, sub_font, "topright"
        )
        if max(scores) >= 3:
            winner = players[0]["name"] if scores[0] > scores[1] else players[1]["name"]
            add_text(f"MATCH WINNER: {winner}", (976, 410), GREEN, sub_font, "topright")
        else:
            add_text("FIRST TO 3 ROUND WINS", (976, 410), MUTED, small_font, "topright")

        add_text(status, (36, 450), AMBER if status else MUTED, small_font)
        buttons = build_buttons()
        for b in buttons:
            b.draw(canvas, font)

        # Fit Design canvas to window
        scaled = pygame.transform.smoothscale(canvas, (max(1, sw), max(1, sh)))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and active_name is not None:
                idx = active_name
                if event.key == pygame.K_RETURN:
                    active_name = None
                    status = "Player name saved."
                elif event.key == pygame.K_ESCAPE:
                    active_name = None
                    status = "Name edit cancelled."
                elif event.key == pygame.K_BACKSPACE:
                    players[idx]["name"] = players[idx]["name"][:-1]
                elif (
                    event.unicode
                    and event.unicode.isprintable()
                    and len(players[idx]["name"]) < 16
                ):
                    players[idx]["name"] += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # translate window coordinates back to 1024x600 design coordinates
                pos = (
                    int(event.pos[0] * WIDTH / max(1, sw)),
                    int(event.pos[1] * HEIGHT / max(1, sh)),
                )
                for b in buttons:
                    if b.clicked(pos):
                        action = b.action
                        kind = action[0]
                        if kind == "char_prev":
                            i = action[1]
                            players[i]["character"] = CHARACTERS[
                                (CHARACTERS.index(players[i]["character"]) - 1)
                                % len(CHARACTERS)
                            ]
                            status = f"Player {i+1} character changed."
                        elif kind == "char_next":
                            i = action[1]
                            players[i]["character"] = CHARACTERS[
                                (CHARACTERS.index(players[i]["character"]) + 1)
                                % len(CHARACTERS)
                            ]
                            status = f"Player {i+1} character changed."
                        elif kind in ("color_prev", "color_next"):
                            i = action[1]
                            names = list(COLORS)
                            step = -1 if kind == "color_prev" else 1
                            players[i]["color"] = names[
                                (names.index(players[i]["color"]) + step) % len(names)
                            ]
                            status = f"Player {i+1} trail color changed."
                        elif kind == "edit_name":
                            active_name = action[1]
                            players[active_name]["name"] = ""
                            status = f"Typing name for Player {active_name+1}; press Enter to finish."
                        elif kind == "start":
                            save_players(players)
                            status = "Settings saved. Game engine integration comes in Part 2."
                        elif kind == "play_again":
                            scores = [0, 0]
                            round_number = 1
                            status = "New match ready. Player settings retained."
                        elif kind == "restart":
                            scores = [0, 0]
                            round_number = 1
                            players = [p.copy() for p in DEFAULT_PLAYERS]
                            active_name = None
                            status = "Match and player settings reset to defaults."
                        elif kind == "score":
                            i = action[1]
                            if max(scores) >= 3:
                                status = "Match complete. Select PLAY AGAIN."
                            else:
                                scores[i] += 1
                                round_number = min(5, round_number + 1)

                                if scores[i] == 3:
                                    status = f"{players[i]['name']} wins the match"
                                else:
                                    status = f"Round awarded to {players[i]['name']}."
                        elif kind == "exit":
                            running = False
                        break

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
