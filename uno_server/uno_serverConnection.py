import asyncio
import websockets
import json
import requests

class GameStatus:
    startedGame = False
    your_turn = False
    top_discard = []
    number_of_handcards = 0
    player_id = None
    current_player = None
    your_handcards = []
    players = []

def fetch_getNumberOfHandcard(player_name, host="http://uno.cylos.net:8000"):
    url = f"{host}/state"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("players", [])
            for numberOfHandCards in data:
                if numberOfHandCards['name'] == player_name:
                    return numberOfHandCards['no_of_cards']
    
    except Exception as e:
        print(f'Fehler:', e)
    
    return None

def fetch_getHandcards(player_id, host="http://uno.cylos.net:8000"):
    url = f"{host}/hand/{player_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("hand", [])
    except Exception as e:
        print("Fehler beim Laden der Handkarten:", e)
    return []

def fetch_getPlayers(host="http://uno.cylos.net:8000"):
    url = f"{host}/state"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("players", [])

            for player in data:
                print(f"{player['name']}")
            
            return data
    
    except Exception as e:
        print("Fehler", e)
    return None

def fetch_getTop_discard(host="http://uno.cylos.net:8000"):
    url = f"{host}/state"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("top_discard", [])
            print(f"top_discard: {data['color']}, {data['value']}")
            return data
    
    except Exception as e:
        print("Fehler", e)
    return None

def action_playCard(player_id, color, value, host="http://uno.cylos.net:8000"):
    url = f"{host}/play/{player_id}/{color}/{value}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
    
            if data.get("status") == "card_played":
                print("Karte wurde gespielt.")
    except Exception as e:
        print("Fehler:", e)
    
    return None

def action_drawCard(player_id, host="http://uno.cylos.net:8000"):
    url = f"{host}/draw/{player_id}"
    print(f"Die Player ID lautet {player_id}")
    try:
        response = requests.get(url)
        print(f"GET {url}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        if response.status_code == 200:
            data = response.json()
            if 'card' in data:
                return data['card']
    
    except Exception as e:
        print("fehler:", e)
    return None

async def websocket_client(player_name: str):
    url = f"ws://52.7.244.208:8000/ws/{player_name}"
    async with websockets.connect(url) as websocket:
        print(f"Verbunden als {player_name}")
        try:
            while True:
                raw = await websocket.recv()
                data = json.loads(raw)
                print("Empfangen:", data)

                if data.get("event") == "join_success":
                    GameStatus.player_id = data["data"]["id"]

                GameStatus.top_discard = fetch_getTop_discard()
                GameStatus.number_of_handcards = fetch_getNumberOfHandcard(player_name)

                # Events
                event = data.get("event")
                if event == "game_started":
                    GameStatus.startedGame = True    

                    if GameStatus.player_id:
                        GameStatus.your_handcards = fetch_getHandcards(GameStatus.player_id)
                        for card in GameStatus.your_handcards:
                            print(f" {card['color']} {card['value']}")

                elif event == "your_turn":
                        GameStatus.your_turn = True

                        # CODE FÜR MAIN

                        card = action_drawCard(GameStatus.player_id)
                        if card:
                            GameStatus.your_handcards = fetch_getHandcards(GameStatus.player_id)
                            print(f"Gezogene Karte: {card['color']} {card['value']}")

                        #BIS HIER    


                GameStatus.players = fetch_getPlayers()
                

                print(f'''
    GameStatus.startedGame \t{GameStatus.startedGame}
    GameStatus.your_turn \t{GameStatus.your_turn}
    GameStatus.your_handcards \t{GameStatus.your_handcards}
    GameStatus.number_of_handcards \t{GameStatus.number_of_handcards}
    GameStatus.top_discard \t{GameStatus.top_discard}
    GameStatus.players \t{GameStatus.players}
    GameStatus.player_id \t{GameStatus.player_id}
                ''')

                
        except websockets.exceptions.ConnectionClosed:
            print("Verbindung geschlossen.")
