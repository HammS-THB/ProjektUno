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

def fetch_handcards(player_id, host="http://uno.cylos.net:8000"):
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

def action_drawCard(player_id, host="http://uno.cylos.net:8000"):
    url = f"{host}/draw/{player_id}"
    print(f"Die Player ID lautet {player_id}")
    try:
        response = requests.get(url)
        print(f"➡️  GET {url}")
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

                # Events
                event = data.get("event")
                if event == "game_started":
                    GameStatus.startedGame = True    

                    if GameStatus.player_id and not GameStatus.your_handcards:
                        GameStatus.your_handcards = fetch_handcards(GameStatus.player_id)
                        for card in GameStatus.your_handcards:
                            print(f" {card['color']} {card['value']}")

                elif event == "your_turn":
                        GameStatus.your_turn = True
                        if GameStatus.player_id:
                            card = action_drawCard(GameStatus.player_id)
                            if card:
                                GameStatus.your_handcards.append(card)
                                print(f"Gezogende Karte: {card['color']} {card['value']}")
                                # Überprüfen ob man eine Karte ziehen will (Button drückt)
                        else:
                            print("Es konnte keine Karte gezogen werden")      


                players = fetch_getPlayers()
                # Überprüfen ob man eine Karte ziehen will (Button drückt)
                

                print(players)
                print(GameStatus.top_discard)

                
        except websockets.exceptions.ConnectionClosed:
            print("Verbindung geschlossen.")
