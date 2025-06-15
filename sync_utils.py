from uno_logic import Card, GameState

def sync_game_with_server(uno, player_name, GS):
    # Spieler synchronisieren
    uno.players = [CardPlayerData(p["name"], p["no_of_cards"], p, player_name, GS.your_handcards)
                   for p in GS.players]

    # Ablagestapel
    if GS.top_discard:
        top = GS.top_discard
        uno.discard_pile = [Card(top["color"], top["value"])]

    # Aktueller Spieler
    for i, player in enumerate(uno.players):
        if player.name == GS.current_player:
            uno.current_player = i
            break

class CardPlayerData:
    def __init__(self, name, no_cards, pdata, me, myhand):
        from uno_logic import Player
        self.name = name
        self.obj = Player(name)
        if name == me:
            self.obj.hand = [Card(c["color"], c["value"]) for c in myhand]
        else:
            self.obj.hand = [Card("Gray", "?") for _ in range(no_cards)]

    def __getattr__(self, attr):
        return getattr(self.obj, attr)
