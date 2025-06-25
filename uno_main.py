# I - Import ...
import asyncio
import os
import re
import threading

import pygame

from uno_logic import Uno, GameState, Card
from uno_server.uno_serverConnection import websocket_client as ws
from uno_server.uno_serverConnection import (
    GameStatus,
    action_drawCard,
    action_playCard,
    fetch_getHandcards,
    fetch_getTop_discard
)


# ... und Initialisierung
pygame.init()


# D - Display-Konfiguration
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UNO - Verbindung")
clock = pygame.time.Clock()


# E - Entities
# Schrift
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

# Farben
RED = (255,0,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,255,0)
GRAY = (200, 200, 200)

# Bilder laden
player_img = pygame.transform.scale(pygame.image.load("templates/Player.png"), (105, 105))
not_found_img = pygame.transform.scale(pygame.image.load("templates/PlayerNotThere.png"), (100, 100))

# Spielobjekte
uno = Uno(["Player1", "Player2"])
input_box = pygame.Rect(250, 260, 300, 50)
draw_pile = pygame.Rect(WIDTH // 2 + 50, HEIGHT // 2 - 45, 60, 90)


# A - Actions
# Hilfsfunktionen
def convert_handcards(dict_list):
    return [Card(card['color'], card['value']) for card in dict_list]


def convert_to_card(card_dict):
    return Card(card_dict["color"], card_dict["value"]) if card_dict else None


def create_card_surface(card):
    try:
        path = card.display_cards()
        if path and os.path.exists(path):
            return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (60, 90))
    except Exception as e:
        print("Fehler beim Laden der Karte:", e)

    surface = pygame.Surface((60, 90))
    surface.fill(GRAY)
    pygame.draw.rect(surface, BLACK, surface.get_rect(), 2)
    surface.blit(font.render("?", True, BLACK), (5, 5))
    return surface


def draw_text(text, rect, color=WHITE, font=font, center=True):
    surface = font.render(text, True, color)
    if center:
        text_rect = surface.get_rect(center=rect.center)
    else:
        text_rect = surface.get_rect(midleft=(rect.x + 10, rect.y + rect.height // 2))
    screen.blit(surface, text_rect)


def websocket_thread(player_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ws(player_name))


def play_card(card):
    if not GameStatus.your_turn:
        return

    try:
        async def play():
            await action_playCard(GameStatus.player_id, card.color, card.value)
            GameStatus.your_handcards = await fetch_getHandcards(GameStatus.player_id)
            top = fetch_getTop_discard()
            if top:
                GameStatus.top_discard = top

        asyncio.run(play())
    except:
        pass


def draw_card():
    if not GameStatus.your_turn:
        return

    try: 
        async def draw():
            await action_drawCard(GameStatus.player_id)
            return await fetch_getHandcards(GameStatus.player_id)

        GameStatus.your_handcards = asyncio.run(draw())

        if len(GameStatus.your_handcards) > 18:
            GameStatus.your_turn = False
            draw_text("Verloren! Zu viele Karten.", pygame.Rect(0, 50, WIDTH, 50))
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit()
            exit()
    except:
        pass


# A - Assign values to key variable
# Status
state = "name_input"
player_name = ""
error_message = ""
ws_thread = None
connected_players = []
card_rects = []

hand = []
prev_hand = []
top_card = None
prev_top_card = None
running = True

# L - Hauptloop
while running:
    screen.fill(RED)

    if state == "name_input":
        draw_text("Wie heisst du?", pygame.Rect(0, 150, WIDTH, 50))
        pygame.draw.rect(screen, WHITE, input_box, 2)
        draw_text(player_name, input_box, font=small_font, center=False)
        if error_message:
            draw_text(error_message,
                      pygame.Rect(0, 330, WIDTH, 30),
                      color=BLACK,
                      font=small_font)

    elif state == "lobby":
        draw_text("UNO - Lobby", pygame.Rect(0, 50, WIDTH, 50))
        draw_text("Warte auf Spieler...", pygame.Rect(0, 100, WIDTH, 40), font=small_font)

        for i, pos in enumerate([(200, 200), (500, 200)]):
            img = player_img if i < len(connected_players) else not_found_img
            name = connected_players[i] if i < len(connected_players) else "Warten..."
            screen.blit(img, pos)
            draw_text(name, pygame.Rect(pos[0] - 30, pos[1] + 110, 150, 40), font=small_font)

        if GameStatus.startedGame:
            state = "game"

    elif state == "game":
        try:
            hand = convert_handcards(GameStatus.your_handcards)
        except:
            hand = prev_hand

        try:
            top_card = convert_to_card(GameStatus.top_discard)
        except:
            top_card = prev_top_card

        pygame.draw.rect(screen, GRAY, draw_pile)
        pygame.draw.rect(screen, BLACK, draw_pile, 2)

        if top_card and top_card is not None:
            screen.blit(create_card_surface(top_card),
                        (WIDTH // 2 - 30, HEIGHT // 2 - 45))

        card_rects.clear()
        if hand:
            for i, card in enumerate(hand):
                x, y = 80 + (i % 9) * 70, HEIGHT - 220 + (i // 9) * 110
                screen.blit(create_card_surface(card), (x, y))
                card_rects.append((pygame.Rect(x, y, 60, 90), i))
        try:
            for player in GameStatus.players:
                if player["name"] != player_name:
                    for i in range(player["no_of_cards"]):
                        x, y = (300 + (i % 15) * 70) / 2, (HEIGHT / 2 - 140 + (i // 15) * 110) / 2
                        pygame.draw.rect(screen, BLACK,
                                         pygame.draw.rect(screen, GRAY, (x, y, 30, 45)), 1)

                    if player.get("no_of_cards",0) == 1:
                        draw_text( "UNO!", pygame.Rect(x, y-20, 60, 20), small_font, center=True)
        except:
            pass

        if GameStatus.your_turn:
            draw_text("Du bist dran", pygame.Rect(20, 20, 300, 40), font=small_font)

        if not GameStatus.your_turn:
            draw_text("Gegner ist dran", pygame.Rect(20, 20, 300, 40), font=small_font)

        if GameStatus.your_handcards == 0:
            draw_text("Du hast gewonnen!", pygame.Rect(0, 50, WIDTH, 50), color=GREEN)
            GameStatus.your_turn = False
            uno.status = GameState.GAME_OVER

        if uno.status == GameState.GAME_OVER:
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit()
            exit()

    # E - Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and state == "name_input":
            if event.key == pygame.K_RETURN:
                if player_name in [p["name"] for p in GameStatus.players if "name" in p]:
                    error_message = "Spielername bereits vergeben"
                elif len(player_name) >= 3:
                    ws_thread = threading.Thread(target=websocket_thread, args=(player_name,), daemon=True)
                    ws_thread.start()
                    state = "lobby"
                else:
                    error_message = "Mind. 3 Zeichen"
            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            elif re.match(r"[a-zA-Z0-9]", event.unicode) and len(player_name) < 15:
                player_name += event.unicode
                error_message = ""
            else:
                error_message = "Nur Buchstaben und Zahlen erlaubt"

        elif event.type == pygame.MOUSEBUTTONDOWN and state == "game" and uno.status != GameState.GAME_OVER:
            if GameStatus.your_turn:
                if draw_pile.collidepoint(event.pos):
                    draw_card()
                else:
                    for rect, idx in card_rects:
                        if rect.collidepoint(event.pos):
                            try:
                                card = convert_handcards(GameStatus.your_handcards)[idx]
                                top_card = convert_to_card(GameStatus.top_discard)
                            except:
                                pass
                            if top_card and (card.color == top_card.color or
                                             card.value == top_card.value or
                                             top_card.color == "black" or
                                             card.color == "black"):
                                play_card(card)
                            else:
                                print("Karte passt nicht.")
                            break

    if hand:
        prev_hand = hand
    if top_card:
        prev_top_card = top_card
    connected_players = [p["name"] for p in GameStatus.players if "name" in p]


    pygame.display.flip() # R - Refresh display
    clock.tick(60) # T - Timer

pygame.quit()
