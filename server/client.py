import asyncio
import websockets
import pygame
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
clock = pygame.time.Clock()
# TODO: set it up so it dynamically receives the height and width from the server on the initialization call.
# stag = enemy.Enemy("stag", HEIGHT, WIDTH)
# hare = enemy.Enemy("hare", HEIGHT, WIDTH)


# WebSocket Connection
async def connect_to_server():
    async with websockets.connect("ws://localhost:8765") as websocket:
        while True:
            # Send updates to server
            message = "Player position update"
            await websocket.send(message)


            # Receive updates from server
            server_message = await websocket.recv()
            print(f"Received message from server: {server_message}")

            # Update game state based on server messages
            # ...

            # Pygame game loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            pygame.display.flip()
            clock.tick(60)

def update_game(new_message): # new message should be a json IG
    pass # i am thinking for the messages that we recieve a string and then parse it as a json, that seems to be easiest IG, just becuase I want different things to be available.
    HEIGHT = new_message
    WIDTH = new_message
    stag = enemy.Enemy("stag", HEIGHT, WIDTH)
    hare = enemy.Enemy("hare", HEIGHT, WIDTH)
    # get the rest of the agents from this message as well.

# Start client
asyncio.get_event_loop().run_until_complete(connect_to_server())
asyncio.get_event_loop().run_forever()