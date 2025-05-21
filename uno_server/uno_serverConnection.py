import asyncio
import websockets
import json

async def websocket_client(player_name:str):
    url = f"ws://52.7.244.208:8000/ws/{player_name}"
    async with websockets.connect(url) as websocket:
        print(f"Verbunden mit Server als Spieler {player_name}")

        # Empfange Nachrichten vom Server
        try:
            while True:
                message = await websocket.recv()
                print(message)
        except websockets.exceptions.ConnectionClosed:
            print("Verbindung zum Server wurde geschlossen.")


if __name__ == "__main__":
    player_name = input("Gib deinen Namen ein: ")
    asyncio.run(websocket_client(player_name))