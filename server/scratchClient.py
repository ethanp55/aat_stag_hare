import json

import websockets
import asyncio
import pygame

from operator import truediv

import pygame
import sys
import time
from pygame import K_ESCAPE
from gui import player
from gui import enemy
from agents.random_agent import *
from agents.human import *
from environment.world import StagHare
#from agents.alegaatr import AlegAATr
#from agents.dqn import DQNAgent


SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

HEIGHT = 0
WIDTH = 0

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.


from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)


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
            real_msg = json.loads(msg)
            print_board(real_msg)
            pygame.display.update()



def print_board(msg):
    height = None
    width = None
    if "HEIGHT" in msg:
        height = msg["HEIGHT"]
    if "WIDTH" in msg:
        width = msg["WIDTH"]
    if height is not None or width is not None:
        draw_grid(height, width)




def draw_grid(height, width): # draws the grid on every frame just so we have it.
    SCREEN.fill(WHITECOLOR)
    widthOffset = (SCREEN_WIDTH / width)
    heightOffset = (SCREEN_HEIGHT / height)
    for x in range(0, width):
        for y in range(0, height):
            rect = pygame.Rect(x*widthOffset, y*heightOffset, widthOffset, heightOffset)
            pygame.draw.rect(SCREEN, BLACKCOLOR, rect, 1)




if __name__ == "__main__":
    asyncio.run(ws_client())
