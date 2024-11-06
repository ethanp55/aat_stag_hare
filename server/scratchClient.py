import json

import websockets
import asyncio
HEIGHT = None
WIDTH = None

# The main function that will handle connection and communication
# with the server
async def ws_client():

    url = "ws://127.0.0.1:7890"
    # Connect to the server
    async with websockets.connect(url) as ws:
        print("WebSocket: Client Connected.")

        # Create a dictionary to send to the server
        user_data = {"age": 22}

        # Serialize the dictionary to a JSON string
        await ws.send(json.dumps(user_data))

        # Stay alive forever, listen to incoming msgs
        while True:
            msg = await ws.recv()



def print_board(msg):
    print("this is the literal value of message ", msg)



if __name__ == "__main__":
    asyncio.run(ws_client())
