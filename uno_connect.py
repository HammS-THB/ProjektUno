import pygame
import asyncio
import threading
import websockets
import json
import re
import uno_main 

# Pygame-Grundsetup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UNO - Verbindung")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

# Farben
RED, WHITE, BLACK, GREEN = (255, 0, 0), (255, 255, 255), (0, 0, 0), (0, 255, 0)

# Bilder
player_img = pygame.transform.scale(pygame.image.load("Player1.png"), (100, 100))
not_found_img = pygame.transform.scale(pygame.image.load("PlayerNotThere.png"), (100, 100))

# Async vorbereiten
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
threading.Thread(target=loop.run_forever, daemon=True).start()

# Status
state = "name_input"
player_name = ""
player_id = None
connected_players = {}
error_message = ""
input_box = pygame.Rect(250, 260, 300, 50)
start_button = pygame.Rect(300, 450, 200, 60)

# Verbindung
async def connect(name):
    global player_id, connected_players
    try:
        uri = f"ws://localhost:8000/ws/{name}"
        async with websockets.connect(uri) as ws:
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                event = data["event"]
                payload = data["data"]

                if event == "join_success":
                    player_id = payload["id"]
                    connected_players[player_id] = name
                elif event == "player_joined":
                    pname = payload["player_name"]
                    connected_players[pname] = pname
                elif event == "game_started":
                    pygame.time.wait(500)
                    uno_main.start_game(player_id, player_name)
                    break
    except Exception as e:
        print("Verbindungsfehler:", e)

# Text-Helfer
def draw_text(text, rect, color=WHITE, font=font, center=True):
    surface = font.render(text, True, color)
    if center:
        text_rect = surface.get_rect(center=rect.center)
    else:
        text_rect = surface.get_rect(midleft=(rect.x + 10, rect.y + rect.height // 2))
    screen.blit(surface, text_rect)


# Hauptloop
running = True
while running:
    screen.fill(RED)

    if state == "name_input":
        draw_text("Wie heisst du?", pygame.Rect(0, 150, WIDTH, 50), color=WHITE, font=font)
        pygame.draw.rect(screen, WHITE, input_box, 2)
        draw_text(player_name, input_box, color=WHITE, font=small_font, center=False)
        if error_message:
            draw_text(error_message, pygame.Rect(0, 330, WIDTH, 30), color=BLACK, font=small_font)

    elif state == "lobby":
        draw_text("UNO - Lobby", pygame.Rect(0, 50, WIDTH, 50), color=WHITE, font=font)
        draw_text("Warte auf Spieler...", pygame.Rect(0, 100, WIDTH, 40), font=small_font)

        # Eigener Spieler
        screen.blit(player_img, (200, 200))
        draw_text(player_name, pygame.Rect(170, 310, 150, 40), font=small_font)

        # Zweiter Spieler
        if len(connected_players) >= 2:
            other_name = [n for n in connected_players.values() if n != player_name][0]
            screen.blit(player_img, (500, 200))
            draw_text(other_name, pygame.Rect(470, 310, 150, 40), font=small_font)
            pygame.draw.rect(screen, GREEN, start_button)
            draw_text("Spiel starten", start_button, color=BLACK, font=small_font)
        else:
            screen.blit(not_found_img, (500, 200))
            draw_text("Warten...", pygame.Rect(480, 310, 150, 40), font=small_font)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == "lobby" and len(connected_players) >= 2:
                if start_button.collidepoint(event.pos):
                    # sende start_game signal via websocket → am besten in API
                    print("Spiel startet...")
                    running = False

        elif event.type == pygame.KEYDOWN and state == "name_input":
            if event.key == pygame.K_RETURN:
                if len(player_name) >= 3:
                    asyncio.run_coroutine_threadsafe(connect(player_name), loop)
                    state = "lobby"
                else:
                    error_message = "Mind. 3 Zeichen"
            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            else:
                if re.match(r"[a-zA-Z0-9]", event.unicode) and len(player_name) < 15:
                    player_name += event.unicode
                    error_message = ""
                else:
                    error_message = "Nur Buchstaben und Zahlen erlaubt"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
