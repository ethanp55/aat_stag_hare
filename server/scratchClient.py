import websockets
import asyncio


# The main function that will handle connection and communication
# with the server
async def ws_client():
    print("WebSocket: Client Connected.")
    url = "ws://127.0.0.1:7890"
    # Connect to the server
    async with websockets.connect(url) as ws:



        age = input("Your Age: ")
        # Send values to the server
        await ws.send(f"{age}")

        # Stay alive forever, listen to incoming msgs
        while True:
            msg = await ws.recv()
            print(msg)



if __name__ == "__main__":
    asyncio.run(ws_client())
