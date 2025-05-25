import pygame
from uno_logic import Uno, GameState  # deine Datei

# Setup
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UNO")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
RED, BLACK = (255, 0, 0), (0, 0, 0)

# Spielobjekt
uno = Uno(["Player1", "Player2"])  # 2 Spieler

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

# Spiel-Loop
running = True
while running:
    screen.fill(RED)
    current_player = uno.players[uno.current_player]
    hand = current_player.hand
    top_card = uno.get_top_card()

    # Ablagestapel
    if top_card:
        top_surf = create_card_surface(top_card)
        screen.blit(top_surf, (WIDTH // 2 - 30, HEIGHT // 2 - 45))

    # Handkarten
    card_rects = []
    for i, card in enumerate(hand):
        card_surf = create_card_surface(card)
        x = 100 + i * 70
        y = HEIGHT - 130
        screen.blit(card_surf, (x, y))
        card_rects.append((pygame.Rect(x, y, 60, 90), i))

    # Text
    msg = f"{current_player.name} ist dran"
    text = font.render(msg, True, BLACK)
    screen.blit(text, (20, 20))

    if uno.status == GameState.GAME_OVER:
        winner = uno.winner.name
        text = font.render(f"Spiel vorbei! Gewinner: {winner}", True, BLACK)
        screen.blit(text, (WIDTH // 2 - 150, 50))

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and uno.status != GameState.GAME_OVER:
            for rect, idx in card_rects:
                if rect.collidepoint(event.pos):
                    success = uno.playCard(idx)
                    print("Karte gespielt:", success)
                    break

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
