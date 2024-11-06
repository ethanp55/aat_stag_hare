import websockets
import asyncio


# The main function that will handle connection and communication
# with the server
async def ws_client():

    url = "ws://127.0.0.1:7890"
    # Connect to the server
    async with websockets.connect(url) as ws:
        print("WebSocket: Client Connected.")

        age = input("Your Age: ")
        # Send values to the server
        await ws.send(f"{age}")

        # Stay alive forever, listen to incoming msgs
        while True:
            msg = await ws.recv()
            print_board(msg)


def print_board(msg):
    print("this is the literal value of message ", msg)



if __name__ == "__main__":
    asyncio.run(ws_client())
