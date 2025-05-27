import asyncio
import websockets
import json

class GameStatus:
    startedGame = False

async def websocket_client(player_name:str):
    url = f"ws://52.7.244.208:8000/ws/{player_name}"
    async with websockets.connect(url) as websocket:
        print(f"Verbunden mit Server als Spieler {player_name}")

        # Empfange Nachrichten vom Server
        try:
            while True:
                raw_message = await websocket.recv()
                message = json.loads(raw_message)
                print(message)
                
                event = message.get("event")

                #Ab hier kommt der Game Status
                if event == "game_started":
                    GameStatus.startedGame = True
        except websockets.exceptions.ConnectionClosed:
            print("Verbindung zum Server wurde geschlossen.")

