import random


# Spielzustand
class GameState:
    MENU = 0
    GAME = 1
    GAME_OVER = 2


class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __str__(self):
        return f'{self.color} {self.value}'


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw(self, deck, count=1):
        cardsDrawn = []
        for _ in range(count):
            if deck:
                card = deck.pop()
                self.hand.append(card)
                cardsDrawn.append(card)
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
                deck.append(Card(color, value))
                # All values, except for 0 have the same card twice
                if value != 0:
                    deck.append(Card(color, value))

        #for i in range(4):
        #    deck.append(wilds[0])
        #    deck.append(wilds[1])


        #print(deck)
        return deck

    def shuffleDeck(self, deck):
        for cardPos in range(len(deck)):
            randPos = random.randint(0, len(deck)-1)
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
            self.status = GameState.GAME_OVER
            self.winner = player
            return True

        if playedCard.value == 'Skip':
            self.next_player()
        elif playedCard.value == 'Reverse':
            self.direction = -1
        elif playedCard.value == 'Draw Two':
            next_player = self.next_player()
            next_player.draw(self.deck, 2)
            return True
        elif playedCard.value == 'Draw Four':
            next_player = self.next_player()
            next_player.draw(self.deck, 4)
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
    



        
    
