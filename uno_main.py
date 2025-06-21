import pygame
import threading
import os, re
from uno_logic import Uno, GameState, Card
from uno_server.uno_serverConnection import websocket_client as ws
from uno_server.uno_serverConnection import *


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

player_img = pygame.transform.scale(pygame.image.load("Player.png"), (105, 105))
not_found_img = pygame.transform.scale(pygame.image.load("PlayerNotThere.png"), (100, 100))

# Spielobjekt
uno = Uno(["Player1", "Player2"]) 

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
    return [Card(card_dict['color'], card_dict['value']) for card_dict in dict_list]

def convert_to_card(card_dict):
    if card_dict is None:
        return None
    return Card(card_dict["color"], card_dict["value"])

def create_card_surface(card_dict):
    png_path = card_dict.displayCards()
    if png_path and os.path.exists(png_path):
        try:
            img = pygame.image.load(png_path).convert_alpha()
            return pygame.transform.scale(img, (60, 90))
        except Exception as e:
            print("Fehler:", e)
    
    surface = pygame.Surface((60, 90))
    surface.fill((200, 200, 200))
    pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
    msg_surface = font.render("?", True, (0, 0, 0))
    surface.blit(msg_surface, (5, 5))
    return surface

def play_card_from_hand(card_dict):
    action_playCard(GameStatus.player_id, card_dict.color, card_dict.value)
    GameStatus.your_handcards = fetch_getHandcards(GameStatus.player_id)
    # und ggf. auch gleich den Ablagestapel:
    maybe_top = fetch_getTop_discard()
    if maybe_top:
        GameStatus.top_discard = maybe_top

    # Hier unnötig, da hier ja nur Karten gespielt werden und keine neuen gezogen werden
    if len(GameStatus.your_handcards) > 18:
        print("Verloren.")
        GameStatus.your_turn = False
        draw_text("Verloren! Zu viele Karten.", pygame.Rect(0, 50, WIDTH, 50), color=WHITE, font=font)
        raise SystemExit

def draw_card_from_server():
    card_dict = action_drawCard(GameStatus.player_id)
    if card_dict:
        GameStatus.your_handcards.append(card_dict)

    if len(GameStatus.your_handcards) > 18:
        print("Verloren.")
        GameStatus.your_turn = False
        draw_text("Verloren! Zu viele Karten.", pygame.Rect(0, 50, WIDTH, 50), color=WHITE, font=font)
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        exit()


def websocket_thread(player_name_dict):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ws(player_name_dict))

def draw_text(msg_surface, card_rect, color=WHITE, font_obj=font, center=True):
    surface = font_obj.render(msg_surface, True, color)
    if center:
        text_rect = surface.get_rect(center=card_rect.center)
    else:
        text_rect = surface.get_rect(midleft=(card_rect.x + 10, card_rect.y + card_rect.height // 2))
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
        if GameStatus.startedGame:
            state = "game"  # Wechsel in Spielzustand

    # Wemm 2 Spieler beigetreten sind wird startGame auf 1 gesetzt und somit startet das Spiel
    elif state == "game":
        #print(f"Deine ID: {GameStatus.player_id}")
        hand = convert_handcards(GameStatus.your_handcards)
        top_card = convert_to_card(GameStatus.top_discard)
        current_player = fetch_getCurrentPlayer()

        # Ziehstapel
        pygame.draw.rect(screen, GRAY, draw_pile)
        pygame.draw.rect(screen, BLACK, draw_pile, 2)

        # Ablagestapel
        if top_card:
            screen.blit(create_card_surface(top_card), (WIDTH // 2 - 30, HEIGHT // 2 - 45))

        # Handkarten zeichnen
        card_rects.clear()
        for i, card in enumerate(hand):
            row = i // 9
            col = i % 9
            x = 80 + col * 70
            y = (HEIGHT - 220) + row * 110 
            card_surf = create_card_surface(card)
            screen.blit(card_surf, (x, y))
            card_rects.append((pygame.Rect(x, y, 60, 90), i))

        for player in GameStatus.players:
            current_player = fetch_getCurrentPlayer()
            if player["name"] != player_name:
                # msg = f"{player['name']} ist dran"
                num_cards = player["no_of_cards"]
                for i in range(num_cards):
                    row = i // 9
                    col = i % 9
                    x = (300 + col * 70) / 2
                    y = ((HEIGHT / 2 - 140) + row * 110) / 2
                    rect = pygame.draw.rect(screen, GRAY, (pygame.Rect(x, y, 30, 45)))
                    pygame.draw.rect(screen, BLACK, rect, 1)

        msg = ""
        if GameStatus.your_turn: 
            msg = "Du bist dran"
        elif not GameStatus.your_turn:
            msg = f"{current_player} ist dran"
        draw_text(msg, pygame.Rect(20, 20, 300, 40), color=WHITE, font=small_font)
            
        if len(GameStatus.your_handcards) == 0:
            draw_text("Du hast gewonnen!", pygame.Rect(0, 50, WIDTH, 50), color=WHITE, font=font)

        # Spiel vorbei
        if uno.status == GameState.GAME_OVER:
            winner = uno.winner.name
            text = font.render(f"Spiel vorbei! Gewinner: {winner}", True, BLACK)
            screen.blit(text, (WIDTH // 2 - 150, 50))
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit()
            exit()

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
            if GameStatus.your_turn:
                if draw_pile.collidepoint(event.pos):
                    draw_card_from_server()
                else:
                    # Prüfen, ob eine Handkarte angeklickt wurde
                    hand = GameStatus.your_handcards
                    top_card = GameStatus.top_discard
                    for rect, idx in card_rects:
                        if rect.collidepoint(event.pos):
                            card = convert_handcards(GameStatus.your_handcards)[idx]
                            top_card = convert_to_card(GameStatus.top_discard)
                            if not top_card:
                                break
                            if card.color == top_card.color or card.value == top_card.value or top_card.color == 'black' or card.color == "black":
                                play_card_from_hand(card)
                            else:
                                print("Karte passt nicht.")
                            break

    connected_players = [p["name"] for p in GameStatus.players if "name" in p]
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
