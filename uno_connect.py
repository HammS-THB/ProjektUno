import pygame
import asyncio
import threading
import re
from uno_logic import Uno, GameState
from uno_server.uno_serverConnection import websocket_client as ws
import uno_server.uno_serverConnection

# Pygame Setup
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
player_img = pygame.transform.scale(pygame.image.load("Player2.png"), (105, 105))
player_img = pygame.transform.scale(pygame.image.load("Player2.png"), (105, 105))
not_found_img = pygame.transform.scale(pygame.image.load("PlayerNotThere.png"), (100, 100))

# Spielobjekt
uno = Uno(["Player1", "Player2"])  # Beispiel: 2 Spieler

# Farben für Kartenanzeige
card_colors = {
    "Red": (255, 50, 50),
    "Green": (50, 200, 50),
    "Blue": (50, 50, 255),
    "Yellow": (255, 255, 50)
}

def create_card_surface(card):
    color = card_colors.get(card.color, (200, 200, 200))
    surface = pygame.Surface((60, 90))
    surface.fill(color)
    pygame.draw.rect(surface, BLACK, surface.get_rect(), 2)
    label = f"{card.value}"
    text = font.render(label, True, BLACK)
    surface.blit(text, (5, 5))
    return surface

# Status
state = "name_input"
player_name = ""
error_message = ""
ws_thread = None
input_box = pygame.Rect(250, 260, 300, 50)
start_button = pygame.Rect(300, 450, 200, 60)

def websocket_thread(player_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ws(player_name))

def draw_text(text, rect, color=WHITE, font=font, center=True):
    surface = font.render(text, True, color)
    if center:
        text_rect = surface.get_rect(center=rect.center)
    else:
        text_rect = surface.get_rect(midleft=(rect.x + 10, rect.y + rect.height // 2))
    screen.blit(surface, text_rect)

running = True
card_rects = []

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

        # Anderer Spieler
        other_names = [n for n in connected_players.values() if n != player_name]
        if other_names:
            screen.blit(player_img, (500, 200))
            draw_text(other_names[0], pygame.Rect(470, 310, 150, 40), font=small_font)
        else:
            screen.blit(not_found_img, (500, 200))
            draw_text("Warten...", pygame.Rect(480, 310, 150, 40), font=small_font)

        # Start-Button
        if len(connected_players) >= 2:
            pygame.draw.rect(screen, GREEN, start_button)
            draw_text("Spiel starten", start_button, color=BLACK, font=small_font)

    # Wemm 2 Spieler beigetreten sind wird startGame auf 1 gesetzt und somit startet das Spiel
    elif uno_server.uno_serverConnection.GameStatus.startedGame:
        if player_join == 1:
            #draw_text("UNO - Lobby", pygame.Rect(0, 50, WIDTH, 50), color=WHITE, font=font)
            draw_text("Spiel wird gestartet", pygame.Rect(0, 100, WIDTH, 40), font=small_font)



            #SCREEN BLIT FEHLT!!!!!!!!!!!!





            time.sleep(2)
            # Eigener Spieler
            #screen.blit(player_img, (200, 200))
            #draw_text(player_name, pygame.Rect(170, 310, 150, 40), font=small_font)


            #other_name = [n for n in connected_players.values() if n != player_name][0]
            #screen.blit(player_img, (500, 200))
            #draw_text(other_name, pygame.Rect(470, 310, 150, 40), font=small_font)
            #pygame.draw.rect(screen, GREEN, start_button)
            #draw_text("Spiel starten", start_button, color=BLACK, font=small_font)

            
            player_join = 0

        elif player_join == 0:
            current_player = uno.players[uno.current_player]
            hand = current_player.hand
            top_card = uno.get_top_card()

        # Ablagestapel
        if top_card:
            top_surf = create_card_surface(top_card)
            screen.blit(top_surf, (WIDTH // 2 - 30, HEIGHT // 2 - 45))

        # Handkarten zeichnen
        card_rects.clear()
        for i, card in enumerate(hand):
            card_surf = create_card_surface(card)
            x = 100 + i * 70
            y = HEIGHT - 130
            screen.blit(card_surf, (x, y))
            card_rects.append((pygame.Rect(x, y, 60, 90), i))

        # Anzeige, wer dran ist
        current = uno_server.uno_serverConnection.GameStatus.current_player
        if current is not None:
            if current == player_name:
                msg = "Du bist dran"
            else:
                msg = f"{current} ist dran"
            text = font.render(msg, True, BLACK)
            screen.blit(text, (20, 20))

        # Spiel vorbei
        if uno.status == GameState.GAME_OVER:
            winner = uno.winner.name
            text = font.render(f"Spiel vorbei! Gewinner: {winner}", True, BLACK)
            screen.blit(text, (WIDTH // 2 - 150, 50))
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and state == "name_input":
            if event.key == pygame.K_RETURN:
                if len(player_name) >= 3:
                    ws_thread = threading.Thread(target=websocket_thread, args=(player_name,), daemon=True)
                    ws_thread.start()
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

        elif event.type == pygame.MOUSEBUTTONDOWN and state == "game" and uno.status != GameState.GAME_OVER:
            for rect, idx in card_rects:
                if rect.collidepoint(event.pos):
                    success = uno.playCard(idx)
                    print("Karte gespielt:", success)
                    break

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
