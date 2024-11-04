import asyncio
import websockets
import pygame
from websockets.asyncio.client import connect

import enemy


from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)

# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((800, 600))



# WebSocket Connection
async def connect_to_server():
    async with websockets.connect("ws://localhost:8765") as websocket:
        message = "We are here! we are here!"
        await websocket.send(message)

        while True:
            server_message = await websocket.recv() # make sure we receive the message
            print(f"Received message from server: {server_message}")
            # we will then need to parse the message and go from there

            pygame.display.flip()
            # decipher messages and




            # Send updates to server
            message = "Player position update"
            await websocket.send(message)





def update_game(new_message): # new message should be a json IG
    pass # i am thinking for the messages that we recieve a string and then parse it as a json, that seems to be easiest IG, just becuase I want different things to be available.
    HEIGHT = new_message
    WIDTH = new_message
    stag = enemy.Enemy("stag", HEIGHT, WIDTH)
    hare = enemy.Enemy("hare", HEIGHT, WIDTH)
    # get the rest of the agents from this message as well.

# Start client



if __name__ == "__main__":
    connect_to_server()
    #asyncio.run_until_complete(connect_to_server())
    #asyncio.get_event_loop().run_forever()
