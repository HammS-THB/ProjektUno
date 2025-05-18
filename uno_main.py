# Import initialisieren
import time
import pygame
import sys
import random

# PyGame initialisieren
pygame.init()

# D - Display configuration
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('UNO')
# bg = pygame.image.load('./background1.png')

# Musik & Sounds
# pygame.mixer.music.load('./bgmusic.mp3')
# pygame.mixer.music.play(-1)
# pygame.mixer.music.set_volume(0.2)

# E - Entities
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
    def __init__(self, color, value):
        self.color = color
        self.value = value


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw(self, deck, count=1):
        cardsDrawn = []
        for _ in range(count):
            if deck:
                self.hand.append(deck.pop())
                cardsDrawn.append(deck.pop())
        return cardsDrawn

    def can_play(self, card, top_card):
        return (card.color == top_card.color or
                card.value == top_card.value)
                #or card.color == 'Wild')

    def play_card(self, card_index):
        if 0 <= card_index < len(self.hand):
            return self.hand.pop(card_index)
        return None


class Uno:
    def __init__(self, player_names):
        self.players = [Player(name) for name in player_names]
        self.deck = self.buildDeck()
        self.shuffleDeck(self.deck) # Deck mischen
        self.discard_pile = [] # Ablagestapel
        self.current_player = 0
        self.direction = 1 # 1 für im Uhrzeiger, -1 für entgegen dem Uhrzeigersinn
        self.status = GameState.GAME
        self.winner = None

        # Am Anfang der Runde werden 7 Karten ausgeteilt
        for player in self.players:
            player.draw(self.deck, 7)

        first_card = self.deck.pop()
        self.discard_pile.append(first_card)

    def buildDeck(self):
        deck = []

        # example card: Red 7, [color] [number]
        colors = ['Red', 'Yellow', 'Green', 'Blue']
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'Skip', 'Reverse', 'Draw Two', 'Draw Four']
        #wilds = ['Wild', 'Wild Draw Four']
        
        for color in colors:
            for value in values:
                cardVal = '{} {}'.format(color, value)
                deck.append(cardVal)
                # All values, except for 0 have the same card twice
                if value != 0:
                    deck.append(cardVal)

        #for i in range(4):
        #    deck.append(wilds[0])
        #    deck.append(wilds[1])


        #print(deck)
        return deck

    def shuffleDeck(self, deck):
        for cardPos in range(len(deck)):
            randPos = random.randint(0, 107)
            deck[cardPos], deck[randPos] = deck[randPos], deck[cardPos]

        print(deck)
        return deck
    
    def get_top_card(self):
        if self.discard_pile:
            return self.discard_pile[-1]
        return None

    def next_player(self):
        self.current_player = (self.current_player + self.direction) % len(self.players)
        return self.players[self.current_player]
    
    def playCard(self, card_index):
        player = self.players[self.current_player]

        card = player.hand[card_index]
        topCard = self.get_top_card()

        if not player.can_play(card, topCard):
            return False
        
        playedCard = player.play_card(card_index)
        self.discard_pile.append(playedCard)

        if len(player.hand) == 0:
            self.status == GameState.GAME_OVER
            self.winner = player
            return True

        if playedCard.value == 'Skip':
            self.next_player()
        elif playedCard.value == 'Reverse':
            self.direction = -1
        elif playedCard.value == 'Draw Two':
            self.next_player.draw(self.deck, 2)
            return True
        elif playedCard.value == 'Draw Four':
            self.next_player.draw(self.deck, 4)
            return True
        else:
            self.next_player()

        return True
    
    def drawCard(self):
        player = self.players[self.current_player]
        cards = player.draw(self.deck, 1)

        if not self.deck and len(self.discard_pile) > 1:
            top_card = self.discard_pile.pop()
            self.deck = self.discard_pile
            self.discard_pile = [top_card]
            self.shuffleDeck()

        self.next_player()
        return cards


# Buttons
cat_btn = Button(300, 390, 150, 50, 'Katze wählen', (255,140,234), (255,0,208))
dog_btn = Button(550, 390, 150, 50, 'Hund wählen', (150,177,255), (0, 64, 255))

# Hauptspiel-Schleife
running = True
clock = pygame.time.Clock()

interactive_item = None
last_item_time = time.time()
item_cooldown = random.uniform(5, 15)

# L - Set up main loop
while running:
    mouse_pos = pygame.mouse.get_pos()
    click = False

    mice_cat = pygame.image.load('./cat/mice.png').convert_alpha()
    sleep_cat = pygame.image.load('./cat/sleep_place.png').convert_alpha()
    sleep_cat = pygame.transform.scale(sleep_cat, (100, 80))
    food_cat = pygame.image.load('./cat/food_bowl.png').convert_alpha()
    food_cat = pygame.transform.scale(food_cat, (100, 80))

    sweets_dog = pygame.image.load('./dog/dogfood.png').convert_alpha()
    sleep_dog = pygame.image.load('./dog/sleep_place.png').convert_alpha()
    sleep_dog = pygame.transform.scale(sleep_dog, (100, 80))
    food_dog = pygame.image.load('./dog/food_bowl.png').convert_alpha()
    food_dog = pygame.transform.scale(food_dog, (100, 80))

    # T - Timer to set frame rate
    clock.tick(60)

    # E - Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if current_state == GameState.GAME and selected_pet:
            # Haustier-Events behandeln
            if selected_pet.handle_event(event):
                continue

        # Taste drücken
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = True

    # Bildschirm löschen
    screen.blit(bg, (0, 0))

    # Menu-Zustand
    if current_state == GameState.MENU:
        font = pygame.font.SysFont(None, 48)
        title = font.render('Pet Game', True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 300))

        # buttons erstellen und überprüfen
        cat_btn.check_hover(mouse_pos)
        dog_btn.check_hover(mouse_pos)

        cat_btn.draw(screen)
        dog_btn.draw(screen)

        if cat_btn.is_clicked(mouse_pos, click):
            selected_pet = Pet('cat')
            current_state = GameState.GAME
        elif dog_btn.is_clicked(mouse_pos, click):
            selected_pet = Pet('dog')
            current_state = GameState.GAME

    # Spiel-Zustand
    elif current_state == GameState.GAME:
        # Aktualisiere Status des Haustiers
        selected_pet.update()
        
        # Moneyanzeige
        font = pygame.font.SysFont(None, 32)
        money_text = font.render(f'Geld: {money}€', True, BLACK)
        screen.blit(money_text, (WIDTH - 150, 20))

        if selected_pet.pet_type == 'cat':
            screen.blit(sleep_cat, (100, 630))
            screen.blit(food_cat, (840, 470))
        elif selected_pet.pet_type == 'dog':
            screen.blit(sleep_dog, (100, 630))
            screen.blit(food_dog, (840, 470))

        if interactive_item is None:
            if selected_pet.pet_type == 'cat':
                interactive_item = InteractiveItem('mice')
            else:
                interactive_item = InteractiveItem('dogfood')

        current_time = time.time()
        if not interactive_item.activate and current_time - last_item_time > item_cooldown:
            interactive_item.appear()
            last_item_time = current_time
            item_cooldown = random.uniform(5, 15)

        if interactive_item:
            interactive_item.update()
            if interactive_item.check_clicked(mouse_pos, click, selected_pet):
                last_item_time = current_time
            interactive_item.draw(screen)

        # Haustier auf dem Screen zeigen
        selected_pet.draw(screen)    


    # Game-Over-Zustand
    elif current_state == GameState.GAME_OVER:
        font = pygame.font.SysFont(None, 82)
        game_over_text = font.render('Game Over', True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))

        font_small = pygame.font.SysFont(None, 46)
        info_text = font_small.render("Drücke ESC zum Beenden oder R für Neustart", True, BLACK)
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT // 2 + 10))

        # Tastencheck
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        elif keys[pygame.K_r]:
            selected_pet = None
            money = 100 
            current_state = GameState.MENU

    # R - Refresh display
    # Bildschirm aktualisieren
    pygame.display.flip()
    #clock.tick(60)

# PyGame beenden
pygame.quit()
sys.exit()