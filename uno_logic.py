import os

class GameState:
    MENU = 0
    GAME = 1
    GAME_OVER = 2

class Card:
    def __init__(self, color, value, filepath='templates_new'):
        self.color = color
        self.value = value
        self.filepath = filepath

    def displayCards(self):
        goal = f"{self.color}_{str(self.value).replace(' ', '_')}.png"

        for data in os.listdir(self.filepath):
            if data.lower() == goal.lower():
                return os.path.join(self.filepath, data)

        return None
    
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw(self, deck, count=1):
        for _ in range(count):
            if deck:
                self.hand.append(deck.pop())

    def can_play(self, card, top_card):
        if card.color == "black":
            return True
        return top_card and (card.color == top_card.color or card.value == top_card.value or top_card.color == "black")

    def play_card(self, index):
        if 0 <= index < len(self.hand):
            return self.hand.pop(index)
        return None

class Uno:
    def __init__(self, player_names):
        from random import shuffle
        self.players = [Player(name) for name in player_names]
        self.deck = self.buildDeck()
        shuffle(self.deck)
        self.discard_pile = []
        self.current_player = 0
        self.status = GameState.GAME
        self.winner = None

        for p in self.players:
            p.draw(self.deck, 7)

        self.discard_pile.append(self.deck.pop())

    def buildDeck(self):
        deck = []
        colors = ["Red", "Yellow", "Green", "Blue"]
        values = list(range(10)) + ["Skip", "Reverse", "Draw Two"]
        for c in colors:
            for v in values:
                deck.append(Card(c, v))

        for _ in range(4):
            deck.append(Card("black", "+4"))
        return deck

    def get_top_card(self):
        return self.discard_pile[-1] if self.discard_pile else None

    def playCard(self, idx):
        pl = self.players[self.current_player]
        card = pl.hand[idx]
        if not pl.can_play(card, self.get_top_card()):
            return False
        self.discard_pile.append(pl.play_card(idx))
        if not pl.hand:
            self.status = GameState.GAME_OVER
            self.winner = pl
        else:
            self.current_player = (self.current_player + 1) % len(self.players)
        return True
