import pygame
import asyncio
import threading
import re
import os
from uno_logic import Uno, GameState, Card
import uno_server.uno_serverConnection
from uno_server.uno_serverConnection import websocket_client as ws
from uno_server.uno_serverConnection import action_playCard, action_drawCard


# Pygame Setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UNO - Verbindung")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

# Farben
RED, WHITE, BLACK, GREEN, GRAY = (255, 0, 0), (255, 255, 255), (0, 0, 0), (0, 255, 0), (200, 200, 200)

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

input_box = pygame.Rect(250, 260, 300, 50)
start_btn  = pygame.Rect(300, 450, 200, 60)
draw_pile  = pygame.Rect(WIDTH // 2 + 50, HEIGHT // 2 - 45, 60, 90)

def convert_handcards(dict_list):
    return [Card(card['color'], card['value']) for card in dict_list]

def convert_to_card(card_dict):
    if card_dict is None:
        return None
    return Card(card_dict["color"], card_dict["value"])

def create_card_surface(card):
    png_path = card.displayCards()
    if png_path and os.path.exists(png_path):
        try:
            img = pygame.image.load(png_path).convert_alpha()
            return pygame.transform.scale(img, (60, 90))
        except Exception as e:
            print("Fehler:", e)
    
    surface = pygame.Surface((60, 90))
    surface.fill((200, 200, 200))
    pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
    text = font.render("?", True, (0, 0, 0))
    surface.blit(text, (5, 5))
    return surface

def play_card_from_hand(card):
    action_playCard(uno_server.uno_serverConnection.GameStatus.player_id, card.color, card.value)

def draw_card_from_server():
    action_drawCard(uno_server.uno_serverConnection.GameStatus.player_id)

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

# Status
state = "name_input"
player_name = ""
error_message = ""
ws_thread = None
connected_players = []
card_rects = []

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

        pos = [(200, 200), (500, 200)]
        name_pos = [pygame.Rect(170, 310, 150, 40), pygame.Rect(470, 310, 150, 40)] 
        player_names = connected_players[:2]
        for i in range(2):
            if i < len(player_names):
                screen.blit(player_img, pos[i])
                draw_text(player_names[i], name_pos[i], color=WHITE, font=small_font)
            else:
                screen.blit(not_found_img, pos[i])
                draw_text("Warten...", name_pos[i], color=WHITE, font=small_font)

         # Warte auf Startsignal vom Server
        if uno_server.uno_serverConnection.GameStatus.startedGame:
            state = "game"  # Wechsel in Spielzustand

    # Wemm 2 Spieler beigetreten sind wird startGame auf 1 gesetzt und somit startet das Spiel
    elif state == "game":
        #print(f"Deine ID: {uno_server.uno_serverConnection.GameStatus.player_id}")
        hand = convert_handcards(uno_server.uno_serverConnection.GameStatus.your_handcards)
        top_card = convert_to_card(uno_server.uno_serverConnection.GameStatus.top_discard) 

        # Ziehstapel
        pygame.draw.rect(screen, GRAY, draw_pile)
        pygame.draw.rect(screen, BLACK, draw_pile, 2)

        # Ablagestapel
        if top_card:
            screen.blit(create_card_surface(top_card), (WIDTH // 2 - 30, HEIGHT // 2 - 45))

        # Handkarten zeichnen
        card_rects.clear()
        for i, card in enumerate(hand):
            card_surf = create_card_surface(card)
            x = 100 + i * 70
            y = HEIGHT - 130
            screen.blit(card_surf, (x, y))
            card_rects.append((pygame.Rect(x, y, 60, 90), i))

        # Anzeige, wer dran ist
        current = getattr(uno_server.uno_serverConnection.GameStatus, "current_player", None)
        if current:
            msg = "Du bist dran" if current == uno_server.uno_serverConnection.GameStatus.player_id else f"{current} ist dran"
            draw_text(msg, pygame.Rect(20, 10, 300, 40), color=WHITE, font=small_font)

        if len(uno_server.uno_serverConnection.GameStatus.your_handcards) == 0:
            draw_text("Du hast gewonnen!", pygame.Rect(0, 50, WIDTH, 50), color=WHITE, font=font)

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
                if player_name in connected_players:
                    error_message = "Spielername bereits vergeben"
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
            if uno_server.uno_serverConnection.GameStatus.your_turn:
                if draw_pile.collidepoint(event.pos):
                    draw_card_from_server()
                else:
                    # Prüfen, ob eine Handkarte angeklickt wurde
                    hand = uno_server.uno_serverConnection.GameStatus.your_handcards
                    top_card = uno_server.uno_serverConnection.GameStatus.top_discard
                    for rect, idx in card_rects:
                        if rect.collidepoint(event.pos):
                            card = convert_handcards(uno_server.uno_serverConnection.GameStatus.your_handcards)[idx]
                            top_card = convert_to_card(uno_server.uno_serverConnection.GameStatus.top_discard)
                            if not top_card:
                                break
                            if card.color == top_card.color or card.value == top_card.value or top_card.color == 'black':
                                play_card_from_hand(card)
                            else:
                                print("Karte passt nicht.")
                            break

    connected_players = [p["name"] for p in uno_server.uno_serverConnection.GameStatus.players if "name" in p]
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
