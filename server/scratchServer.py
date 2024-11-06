import websockets
import asyncio

connected_clients = {}


# Creating WebSocket server
async def ws_server(websocket, path):
    client_id = id(websocket)
    connected_clients[client_id] = websocket

    try:
        # Handle first message
        input_data = await websocket.recv()
        print(f"Details Received from Client: {client_id} : {input_data}")
        print(f"Age: {input_data}")
        client_id = id(websocket)
        connected_clients[client_id] = websocket

        if int(input_data) < 18:
            await websocket.send(f"Sorry!, You can't join the club.")
        else:
            await websocket.send(f"Welcome aboard.")

        # Keep connection open
        while True:
            # Wait for future messages
            input_data = await websocket.recv()
            print(f"Received another message: {input_data}")
            # Optionally, process additional messages here

    except websockets.ConnectionClosed as e:
        print(f"Connection with client {client_id} closed: {e}")


async def main():
    async with websockets.serve(ws_server, "localhost", 7890):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
