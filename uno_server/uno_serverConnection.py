import asyncio
import websockets
import json
import httpx

class GameStatus:
    startedGame = False
    your_turn = False
    top_discard = []
    number_of_handcards = 0
    player_id = None
    current_player = None
    your_handcards = []
    players = []

# Asynchrone Version der fetch-Funktionen:

async def fetch_getCurrentPlayer(host="http://uno.cylos.net:8000"):
    url = f"{host}/state"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("current_player")
        except Exception as e:
            print("Fehler:", e)
    return None

async def fetch_getNumberOfHandcard(player_name, host="http://uno.cylos.net:8000"):
    url = f"{host}/state"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json().get("players", [])
                for numberOfHandCards in data:
                    if numberOfHandCards['name'] == player_name:
                        return numberOfHandCards['no_of_cards']
        except Exception as e:
            print(f'Fehler:', e)
    return None

async def fetch_getHandcards(player_id, host="http://uno.cylos.net:8000"):
    url = f"{host}/hand/{player_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json().get("hand", [])
        except Exception as e:
            print("Fehler beim Laden der Handkarten:", e)
    return []

async def fetch_getPlayers(host="http://uno.cylos.net:8000"):
    url = f"{host}/state"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json().get("players", [])
                for player in data:
                    print(f"{player['name']}")
                return data
        except Exception as e:
            print("Fehler", e)
    return None

async def fetch_getTop_discard(host="http://uno.cylos.net:8000"):
    url = f"{host}/state"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                json_data = response.json()
                data = json_data.get("top_discard")
                if isinstance(data, dict):
                    print(f"top_discard: {data.get('color')}, {data.get('value')}")
                    return data
                else:
                    print("top_discard fehlt oder ist ungültig:", data)
        except Exception as e:
            print("Der Fehler:", e)
    return {}


async def action_playCard(player_id, color, value, host="http://uno.cylos.net:8000"):
    url = f"{host}/play/{player_id}/{color}/{value}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "card_played":
                    print("Karte wurde gespielt.")
            GameStatus.your_turn = False
        except Exception as e:
            print("Fehler:", e)
    return None

async def action_drawCard(player_id, host="http://uno.cylos.net:8000"):
    url = f"{host}/draw/{player_id}"
    print(f"Die Player ID lautet {player_id}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            print(f"GET {url}")
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            if response.status_code == 200:
                data = response.json()
                if 'card' in data:
                    return data['card']
                GameStatus.your_turn = True
        except Exception as e:
            print("Fehler:", e)
    return None

# WebSocket Client mit asynchronen Fetch-Funktionen

async def websocket_client(player_name: str):
    url = f"ws://52.7.244.208:8000/ws/{player_name}"
    async with websockets.connect(url) as ws:
        while True:
            raw = await ws.recv()
            data = json.loads(raw)

            if data.get("event") == "join_success":
                GameStatus.player_id = data["data"]["id"]
                GameStatus.players = await fetch_getPlayers()

            await asyncio.sleep(1)

            if data.get("event") == "game_started":
                GameStatus.startedGame = True
                if not GameStatus.your_handcards and not GameStatus.top_discard:
                    GameStatus.your_handcards = await fetch_getHandcards(GameStatus.player_id)
                    GameStatus.top_discard = await fetch_getTop_discard()
                    GameStatus.number_of_handcards = await fetch_getNumberOfHandcard(player_name)
                    GameStatus.current_player = await fetch_getCurrentPlayer()
                    

            elif data.get("event") == "your_turn":
                GameStatus.your_turn = True
                #if not GameStatus.your_handcards and not GameStatus.top_discard:
                #    GameStatus.your_handcards = await fetch_getHandcards(GameStatus.player_id)
                #    GameStatus.top_discard = await fetch_getTop_discard()
            
            elif data.get("event") != "your_turn":
                GameStatus.your_turn = False

            maybe_top = await fetch_getTop_discard()
            if maybe_top:
                GameStatus.top_discard = maybe_top
            
            current_playerChanged = await fetch_getCurrentPlayer()
            if current_playerChanged:
                if current_playerChanged == player_name:
                    GameStatus.your_turn = True

            maybe_handcard = await fetch_getHandcards(GameStatus.player_id)
            if maybe_handcard:
                GameStatus.your_handcards = maybe_handcard
            print(f'''
GameStatus.startedGame \t\t{GameStatus.startedGame}
GameStatus.your_turn \t\t{GameStatus.your_turn}
GameStatus.your_handcards \t{GameStatus.your_handcards}
GameStatus.number_of_handcards \t{GameStatus.number_of_handcards}
GameStatus.top_discard \t\t{GameStatus.top_discard}
GameStatus.players \t\t{GameStatus.players}
GameStatus.player_id \t\t{GameStatus.player_id}
GameStatus.current_player \t{GameStatus.current_player}
            ''')


