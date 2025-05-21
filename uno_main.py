# Import initialisieren
import time
import pygame
import sys
import random
from pygame._sdl2 import Window
from uno_logic import Uno

# PyGame initialisieren
pygame.init()

# D - Display configuration
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
Window.from_display_module().maximize()
pygame.display.set_caption('UNO')

# E - Entities
# Karten 
CARD_WIDTH = 240
CARD_HEIGHT = 360

# Farben
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)

# Spielzustand
class GameState:
    MENU = 0
    GAME = 1
    GAME_OVER = 2

# A - Assign values to key variables
# Spielvariablen
current_state = GameState.MENU

class Card:
    def __init__(self, x, y, width, height, color, value):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.value = value
        self.is_playable = False

    def draw(self, screen):
        color = self.color
        pygame.draw.rect(screen, color, self.rect)

        font = pygame.font.SysFont(None, 40)
        text_surface = font.render(self.value, True, 'black')
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class CardStack:
    def __init__(self, x, y, width, height, color, text, deck):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.deck = deck

    def draw(self, screen):
        color = self.color
        pygame.draw.rect(screen, color, self.rect)

        font = pygame.font.SysFont(None, 30)
        text_surface = font.render(self.text, True, 'black')
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


# Hauptspiel-Schleife
running = True
clock = pygame.time.Clock()

# L - Set up main loop
while running:
    mouse_pos = pygame.mouse.get_pos()
    click = False

    # T - Timer to set frame rate
    clock.tick(60)

    # E - Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Taste drücken
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = True


    # Hintergrundfarbe setzen (z. B. dunkelgrün)
    screen.fill((255,255,255))

    game = Uno(['Spieler1', 'Spieler2'])

    # Beispielkarte erzeugen und zeichnen
    # test_card = Card(100, 100, CARD_WIDTH - 50, CARD_HEIGHT - 50, RED, "7")
    # test_card.draw(screen)

    discard_pile = CardStack(800, 240, CARD_WIDTH - 100, CARD_HEIGHT - 100, 'gray', 'Ablagestapel', game.discard_pile)
    discard_pile.draw(screen)

    draw_pile = CardStack(610, 240, CARD_WIDTH - 100, CARD_HEIGHT - 100, 'gray', 'Ziehstapel', game.get_top_card)
    draw_pile.draw(screen)


    # R - Refresh display
    # Bildschirm aktualisieren
    pygame.display.flip()
    #clock.tick(60)

# PyGame beenden
pygame.quit()
sys.exit()