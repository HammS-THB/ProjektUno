import asyncio
import websockets
import json
import requests

class GameStatus:
    startedGame = False
    your_turn = False
    top_discard = None
    number_of_handcards = 7
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

                if "top_discard" in data:
                    GameStatus.top_discard = data["top_discard"]


                # Events
                event = data.get("event")
                if event == "game_started":
                    GameStatus.startedGame = True

                    if GameStatus.player_id and not GameStatus.your_handcards:
                        GameStatus.your_handcards = fetch_handcards(GameStatus.player_id)
                        for card in GameStatus.your_handcards:
                            print(f" {card['color']} {card['value']}")

                players = fetch_getPlayers()
                print(players)

                if event == "your_turn":
                    GameStatus.your_turn = True
        except websockets.exceptions.ConnectionClosed:
            print("Verbindung geschlossen.")
