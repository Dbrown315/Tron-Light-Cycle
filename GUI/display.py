#
# File: display.py
# Group: Group 9
# Purpose: Create the Graphical User Interface for user interactions and game
#          settings using the Pygame Library.

""" """

import json
import os
import sys
import time
import argparse
from pathlib import Path

import pygame
import asyncio

WIDTH, HEIGHT = 1024, 600
FPS = 60
CONFIG_PATH = Path(__file__).resolve().parent / "config" / "players.json"

BG = (5, 10, 22)
PANEL = (12, 22, 42)
PANEL_ALT = (9, 17, 33)
CYAN = (54, 225, 255)
PINK = (255, 78, 151)
ORANGE = (255, 151, 64)
WHITE = (238, 246, 255)
MUTED = (139, 165, 190)
BORDER = (35, 76, 105)
GREEN = (93, 255, 183)
AMBER = (255, 205, 89)

# Game Characters
CHARACTERS = ["Spider", "Dino", "Ladybird", "Tiger", "Dragonfly", "Ant", "Butterfly"]

# Game Colors: Blue / Orange (defaults)
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
    return pygame.Rect(rect.x + dx, rect.y + dy, rect.w - 2 * dx, rect.h - 2 * dy)


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
    if rect.width <= 0 or rect.height <= 0:
        return
    rendered = font.render(str(content), True, color)

    if rendered.get_width() > rect.width or rendered.get_height() > rect.height:
        factor = min(
            rect.width / max(1, rendered.get_width()),
            rect.height / max(1, rendered.get_height()),
        )
        new_size = max(8, int(font.get_height() * factor))
        fitted = pygame.font.SysFont("dejavusans", new_size, bold=font.get_bold())
        rendered = fitted.render(str(content), True, color)
    destination = rendered.get_rect()
    if align == "center":
        destination.center = rect.center
    elif align == "right":
        destination.midright = rect.midright
    else:
        destination.midleft = rect.midleft

    previous_clip = surface.get_clip()
    surface.set_clip(rect)
    surface.blit(rendered, destination)
    surface.set_clip(previous_clip)


# Layout is defined once, and shared by drawing and mouse hitboxes.
LAYOUT = {
    "header": pygame.Rect(24, 16, 976, 82),
    "player_1": pygame.Rect(24, 110, 478, 222),
    "player_2": pygame.Rect(510, 110, 478, 222),
    "scoreboard": pygame.Rect(24, 344, 976, 88),
    "status": pygame.Rect(24, 440, 976, 30),
    "actions": pygame.Rect(24, 480, 976, 54),
    "footer": pygame.Rect(24, 548, 976, 36),
    "preview": pygame.Rect(686, 476, 56, 56),
}


def player_card(i):
    return LAYOUT["player_1" if i == 0 else "player_2"]


DEFAULT_PLAYERS = [
    {"name": "Player A", "character": "spider", "color": "blue"},
    {"name": "Player B", "character": "dino", "color": "orange"},
]


def load_players():
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list) and len(data) == 2:
            players = []
            for i, p in enumerate(data):
                players.append(
                    {
                        "name": DEFAULT_PLAYERS[i]["name"],
                        "character": (
                            str(p.get("character")).capitalize()
                            if str(p.get("character", "")).capitalize() in CHARACTERS
                            else CHARACTERS[i]
                        ),
                        "color": (
                            p.get("color")
                            if p.get("color") in COLORS
                            else DEFAULT_PLAYERS[i]["color"]
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


async def main(simulate=False, ticks=8, display=0, ble=False):
    # Import from Matrix/Game package;
    repo_root = Path(__file__).resolve().parent.parent
    matrix_dir = repo_root / "Matrix"
    if str(matrix_dir) not in sys.path:
        sys.path.insert(0, str(matrix_dir))
    from Game.engine import Direction
    from Game.session import GameSession
    from Game.input_router import route_input
    from navigation import MenuNavigation
    from name_keyboard import NameKeyboard, ROWS

    # Set display to 1 to view on portable inch screen
    pygame.init()
    pygame.display.set_caption("TRON-Light-Cycle")
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE, display=display)
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("dejavusans", 30, bold=True)
    name_font = pygame.font.SysFont("dejavusans", 23, bold=True)
    sub_font = pygame.font.SysFont("dejavusans", 13, bold=True)
    font = pygame.font.SysFont("dejavusans", 17)
    small_font = pygame.font.SysFont("dejavusans", 13)

    players = load_players()
    renderer = None
    if not simulate:
        try:
            from Game.matrix_renderer import MatrixRenderer

            renderer = MatrixRenderer()
        except Exception:
            pygame.quit()
            raise RuntimeError(
                "Matrix initialization failed; check bonnet/PIO permissions, or run --simulate"
            )
    if players[0]["color"] == players[1]["color"]:
        players[1]["color"] = "orange" if players[0]["color"] != "orange" else "blue"
    session = GameSession(
        colors=tuple(p["color"] for p in players), ticks=ticks, renderer=renderer
    )
    keymap = {
        pygame.K_w: (0, Direction.UP),
        pygame.K_d: (0, Direction.RIGHT),
        pygame.K_s: (0, Direction.DOWN),
        pygame.K_a: (0, Direction.LEFT),
        pygame.K_UP: (1, Direction.UP),
        pygame.K_RIGHT: (1, Direction.RIGHT),
        pygame.K_DOWN: (1, Direction.DOWN),
        pygame.K_LEFT: (1, Direction.LEFT),
    }
    navigation = MenuNavigation()
    ble_queue = asyncio.Queue()
    ble_status_queue = asyncio.Queue()
    ble_connected = {"P1": False, "P2": False}
    receiver_task = None
    if ble:
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from Pi.ble_receiver import run_receiver

        receiver_task = asyncio.create_task(
            run_receiver(ble_queue, status_queue=ble_status_queue)
        )
    active_name = None
    name_editor = None
    status = "Configure riders, then START. WASD=P1, arrows=P2."
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
        for i in range(2):
            card = player_card(i)
            accent = CYAN if i == 0 else ORANGE
            x = card.x + 18
            result.extend(
                [
                    Button(
                        (x, 225, 38, 34), "−", ("color_prev", i), accent, font_size=20
                    ),
                    Button(
                        (x + 48, 225, 38, 34),
                        "+",
                        ("color_next", i),
                        accent,
                        font_size=20,
                    ),
                    Button(
                        (card.right - 134, 155, 114, 34),
                        "EDIT NAME",
                        ("edit_name", i),
                        accent,
                        PANEL_ALT,
                        12,
                    ),
                ]
            )
        result.extend(
            [
                Button((32, 483, 166, 48), "START", ("start",), CYAN, (7, 54, 72), 17),
                Button(
                    (210, 483, 166, 48),
                    "NEXT ROUND",
                    ("play_again",),
                    GREEN,
                    PANEL_ALT,
                    15,
                ),
                Button(
                    (388, 483, 166, 48), "RESTART", ("restart",), AMBER, PANEL_ALT, 17
                ),
                Button((840, 483, 148, 48), "EXIT", ("exit",), PINK, (54, 17, 37), 17),
            ]
        )
        return result

    def dispatch_action(action):
        nonlocal players, active_name, name_editor, status, running
        kind = action[0]
        if session.phase != "ready" and kind in (
            "color_prev",
            "color_next",
            "edit_name",
        ):
            status = (
                "Player settings are locked during a match. Select RESTART to edit."
            )
        elif kind in ("color_prev", "color_next"):
            i = action[1]
            names = list(COLORS)
            step = -1 if kind == "color_prev" else 1
            players[i]["color"] = names[
                (names.index(players[i]["color"]) + step) % len(names)
            ]
            if players[i]["color"] == players[1 - i]["color"]:
                players[i]["color"] = names[
                    (names.index(players[i]["color"]) + step) % len(names)
                ]
            status = f"Player {i+1} trail color changed."
            session.colors = tuple(p["color"] for p in players)
        elif kind == "edit_name":
            active_name = action[1]
            name_editor = NameKeyboard(active_name, players[active_name]["name"])
            # players[active_name]["name"] = ""
            # status = f"Typing name for Player {active_name+1}; press Enter to finish."
            status = f"Editing player {active_name+1}: A=select, B=delete, DONE=save."
        elif kind == "start":
            if session.phase == "ready":
                if players[0]["color"] == players[1]["color"]:
                    status = "Choose different trail colors for both players."
                else:
                    session.colors = tuple(p["color"] for p in players)
                    save_players(players)
                    session.start(time.monotonic())
                    status = "Game started on RGB matrix."
            else:
                status = "Match already started; use NEXT ROUND"
        elif kind == "play_again":
            if session.phase == "match_over":
                session.restart(time.monotonic())
                session.start(time.monotonic())
                status = "New match started; settings retained."
            elif session.phase == "round_over":
                session.start(time.monotonic())
                status = f"Round {session.engine.round_number} started."
            else:
                status = "Finish the current round first."
        elif kind == "restart":
            players = [p.copy() for p in DEFAULT_PLAYERS]
            session.restart(
                time.monotonic(),
                colors=tuple(p["color"] for p in players),
            )
            active_name = None
            name_editor = None
            status = "Match and player settings reset to defaults."
        elif kind == "exit":
            running = False

    def finish_name(commit):
        nonlocal active_name, name_editor, status
        if name_editor is None:
            return
        if commit:
            players[name_editor.player]["name"] = (
                name_editor.value.strip() or f"Player {name_editor.player + 1}"
            )
            status = f"Player {name_editor.player + 1} name saved."
        else:
            status = "Name edit cancelled; previous name retained."
        active_name = None
        name_editor = None

    def keyboard_cells():
        # Overlay occupies the middle  of the screen and is independent of game
        # buttons. Coordinates use 1024x600 canvas units.
        cells = []
        for row_index, keys in enumerate(ROWS):
            for col_index, key in enumerate(keys):
                cells.append(
                    (
                        row_index,
                        col_index,
                        key,
                        pygame.Rect(132 + col_index * 77, 205 + row_index * 67, 70, 56),
                    )
                )
        return cells

    try:
        while running:
            # Let Bleak scanning, notifications and reconnection progress.
            await asyncio.sleep(0)
            navigation.set_phase(session.phase)
            while not ble_status_queue.empty():
                player_id, connected = ble_status_queue.get_nowait()
                if player_id in ble_connected:
                    ble_connected[player_id] = connected
                ble_status_queue.task_done()
            # Snapshot queue size: input arriving later is handled in the next frame
            for _ in range(ble_queue.qsize()):
                event = ble_queue.get_nowait()
                try:
                    if active_name is not None:
                        # TODO: [X] - On-screen name entry
                        if isinstance(event, (tuple, list)) and len(event) == 2:
                            player_id, button = event
                            if player_id == f"P{name_editor.player + 1}":
                                result = name_editor.handle(button)
                                if result in ("done", "cancel"):
                                    finish_name(result == "done")
                        continue
                    action = route_input(
                        event,
                        session.phase,
                        navigation,
                        lambda player, direction: session.steer(
                            player, Direction[direction]
                        ),
                    )
                    if action is not None:
                        dispatch_action(action)
                finally:
                    ble_queue.task_done()
            now = time.monotonic()
            session.update(now)
            for event_info in session.drain_events():
                if event_info.kind == "ROUND_STARTED":
                    status = f"Round {event_info.round_number}"
                elif event_info.kind == "ROUND_FINISHED":
                    winner = event_info.winner
                    status = (
                        "Round drawn. SELECT NEXT ROUND."
                        if winner is None
                        else "{} wins round {}! Select NEXT ROUND.".format(players[winner]["name"], event_info.round_number)
                    )
                elif event_info.kind == "MATCH_FINISHED":
                    status = "MATCH WINNER: {}! Select NEW MATCH.".format(players[event_info.match_winner]["name"])
            session.show(now)
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

            header = LAYOUT["header"]
            pygame.draw.rect(canvas, PANEL, header, border_radius=12)
            pygame.draw.rect(canvas, CYAN, header, 2, border_radius=12)
            draw_fitted_text(canvas, "TRON", title_font, CYAN, (44, 27, 280, 38))
            draw_fitted_text(canvas, "LIGHT CYCLE", sub_font, MUTED, (46, 67, 310, 29))
            if ble:
                for player_id, y in (("P1", 33), ("P2", 63)):
                    connected = ble_connected[player_id]
                    label = f"{player_id}: {'CONNECTED' if connected else 'OFFLINE'}"
                    draw_fitted_text(
                        canvas, label, sub_font,
                        GREEN if connected else MUTED,
                        (810, y, 170, 22), "right"
                    )
            else:
                draw_fitted_text(
                    canvas, "BLE DISABLED", sub_font, MUTED,
                    (810, 42, 170, 24), "right"
                )

            # Player cards: independent name editing and color selection.
            for i in range(2):
                card = player_card(i)
                x = card.x
                accent = CYAN if i == 0 else ORANGE
                p = players[i]
                pygame.draw.rect(canvas, PANEL, card, border_radius=12)
                pygame.draw.rect(canvas, accent, card, 2, border_radius=12)
                draw_fitted_text(
                    canvas, f"PLAYER {i+1}", sub_font, accent, (x + 18, 121, 160, 20)
                )
                draw_fitted_text(
                    canvas,
                    p["name"] or "(enter name)",
                    name_font,
                    WHITE,
                    (x + 18, 147, 300, 37),
                )
                draw_fitted_text(
                    canvas, "COLOR TRAIL", small_font, MUTED, (x + 18, 198, 180, 20)
                )
                draw_fitted_text(
                    canvas,
                    p["color"].upper(),
                    font,
                    COLORS[p["color"]],
                    (x + 116, 226, 210, 32),
                )
                pygame.draw.circle(
                    canvas, COLORS[p["color"]], (card.right - 42, 239), 11
                )
                pygame.draw.circle(canvas, WHITE, (card.right - 42, 239), 11, 1)

            # The engine controls the scores and round numbers.
            scores = session.engine.scores
            round_number = session.engine.round_number
            board = LAYOUT["scoreboard"]
            # Scoreboard
            pygame.draw.rect(canvas, PANEL, board, border_radius=12)
            pygame.draw.rect(canvas, BORDER, board, 2, border_radius=12)
            draw_fitted_text(canvas, "MATCH SCORE", sub_font, MUTED, (42, 351, 230, 20))
            draw_fitted_text(
                canvas,
                players[0]["name"],
                font,
                COLORS[players[0]["color"]],
                (42, 380, 240, 32),
            )
            draw_fitted_text(
                canvas,
                str(scores[0]),
                title_font,
                COLORS[players[0]["color"]],
                (302, 373, 68, 42),
                "center",
            )
            draw_fitted_text(
                canvas, "—", title_font, MUTED, (480, 373, 64, 42), "center"
            )
            draw_fitted_text(
                canvas,
                str(scores[1]),
                title_font,
                COLORS[players[1]["color"]],
                (610, 373, 68, 42),
                "center",
            )
            draw_fitted_text(
                canvas,
                players[1]["name"],
                font,
                COLORS[players[1]["color"]],
                (694, 380, 145, 32),
            )
            draw_fitted_text(
                canvas,
                f"ROUND {round_number} · FIRST TO 3",
                sub_font,
                WHITE,
                (836, 351, 146, 24),
                "right",
            )
            if session.engine.match_winner is not None:
                winner_name = players[session.engine.match_winner]["name"]
                draw_fitted_text(
                    canvas,
                    f"WINNER: {winner_name}",
                    sub_font,
                    GREEN,
                    (832, 386, 150, 28),
                    "right",
                )
            else:
                draw_fitted_text(
                    canvas,
                    "FIRST TO 3 WINS",
                    small_font,
                    MUTED,
                    (832, 386, 150, 28),
                    "right",
                )
            status_rect = LAYOUT["status"]
            pygame.draw.rect(canvas, PANEL_ALT, status_rect, border_radius=6)
            draw_fitted_text(
                canvas, status, small_font, AMBER, inset(status_rect, 12, 4)
            )

            buttons = build_buttons()
            for b in buttons:
                if b.action[0] == "play_again":
                    b.label = (
                        "NEW MATCH" if session.phase == "match_over" else "NEXT ROUND"
                    )
            # Preview window of gameplay
            preview_rect = LAYOUT["preview"]
            preview = pygame.surfarray.make_surface(session.frame(now).swapaxes(0, 1))
            canvas.blit(
                pygame.transform.scale(preview, preview_rect.size), preview_rect
            )
            pygame.draw.rect(canvas, BORDER, preview_rect, 1)
            draw_fitted_text(canvas, "MATRIX", small_font, MUTED, (750, 487, 80, 18))
            draw_fitted_text(canvas, "PREVIEW", small_font, MUTED, (750, 506, 80, 18))
            draw_fitted_text(
                canvas,
                "WASD: P1     ARROWS: P2     SPACE: NEXT    ESC: EXIT",
                small_font,
                MUTED,
                LAYOUT["footer"],
                "center",
            )
            for b in buttons:
                b.draw(canvas, font)
                if ble and active_name is None and session.phase != "playing":
                    for player_idx, position in enumerate(navigation.positions):
                        if b.action == navigation.selected_action(player_idx):
                            accent = CYAN if player_idx == 0 else ORANGE
                            pygame.draw.rect(
                                canvas, accent, b.rect.inflate(6, 6), 2, border_radius=8
                            )

            if name_editor is not None:
                # Opaque overlay prevents GUI controls from being mistaken for
                # keyboard controls.
                shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                shade.fill((2, 6, 14, 220))
                canvas.blit(shade, (0, 0))
                pygame.draw.rect(canvas, PANEL, (96, 94, 832, 414), border_radius=14)
                accent = CYAN if name_editor.player == 0 else ORANGE
                pygame.draw.rect(
                    canvas, accent, (96, 94, 832, 414), 2, border_radius=14
                )
                draw_fitted_text(
                    canvas,
                    f"PLAYER {name_editor.player + 1} - EDIT NAME",
                    name_font,
                    accent,
                    (125, 108, 750, 37),
                )
                pygame.draw.rect(
                    canvas, PANEL_ALT, (125, 151, 750, 44), border_radius=7
                )
                draw_fitted_text(
                    canvas, name_editor.value + "_", font, WHITE, (140, 155, 715, 34)
                )
                for row_i, col_i, key, cell in keyboard_cells():
                    focused = (row_i, col_i) == (name_editor.row, name_editor.col)
                    pygame.draw.rect(
                        canvas,
                        (28, 75, 94) if focused else PANEL_ALT,
                        cell,
                        border_radius=7,
                    )
                    pygame.draw.rect(
                        canvas,
                        accent if focused else BORDER,
                        cell,
                        3 if focused else 1,
                        border_radius=7,
                    )
                    draw_fitted_text(
                        canvas,
                        key,
                        small_font if len(key) > 1 else font,
                        WHITE,
                        cell.inflate(-4, 4),
                        "center",
                    )
                draw_fitted_text(
                    canvas,
                    "D-PAD: MOVE   A: SELECT   B: DELETE   ENTER: SAVE    ESC: CANCEL",
                    small_font,
                    MUTED,
                    (120, 480, 780, 23),
                    "center",
                )

            # Fit Design canvas to window
            scaled = pygame.transform.smoothscale(canvas, (max(1, sw), max(1, sh)))
            screen.blit(scaled, (0, 0))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and name_editor is not None:
                    # idx = active_name
                    if event.key == pygame.K_RETURN:
                        finish_name(True)
                    elif event.key == pygame.K_ESCAPE:
                        finish_name(False)
                    elif event.key == pygame.K_BACKSPACE:
                        name_editor.handle("B")
                    elif event.unicode:
                        name_editor.type_character(event.unicode)
                elif event.type == pygame.KEYDOWN and active_name is None:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in keymap:
                        player_id, direction = keymap[event.key]
                        session.steer(player_id, direction)
                    elif event.key == pygame.K_SPACE and session.phase in (
                        "round_over",
                        "match_over",
                    ):
                        if session.phase == "match_over":
                            session.restart(time.monotonic())
                        session.start(time.monotonic())
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # translate window coordinates back to 1024x600 design coordinates
                    pos = (
                        int(event.pos[0] * WIDTH / max(1, sw)),
                        int(event.pos[1] * HEIGHT / max(1, sh)),
                    )
                    if name_editor is not None:
                        for row_i, col_i, key, cell in keyboard_cells():
                            if cell.collidepoint(pos):
                                name_editor.row, name_editor.col = row_i, col_i
                                result = name_editor.handle("A")
                                if result in ("done", "cancel"):
                                    finish_name(result == "done")
                                break
                    else:
                        for b in buttons:
                            if b.clicked(pos):
                                dispatch_action(b.action)
                                break

        await asyncio.sleep(max(0.001, 1.0 / FPS - (time.monotonic() - now)))

    finally:
        if receiver_task is not None:
            receiver_task.cancel()
            await asyncio.gather(receiver_task, return_exceptions=True)
        session.close()
        pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="GUI and engine without phsical LED matrix",
    )
    parser.add_argument("--ticks", type=float, default=8)
    parser.add_argument(
        "--display",
        type=int,
        default=0,
        help="SDL display index (e.g. 1 for portable screen)",
    )
    parser.add_argument("--ble", action="store_true", help="Enable BLE receiver")
    args = parser.parse_args()
    if not 0 < args.ticks <= 30:
        parser.error("--ticks must be greater than 0 and at most 30")
    asyncio.run(
        main(
            simulate=args.simulate, ticks=args.ticks, display=args.display, ble=args.ble
        )
    )
