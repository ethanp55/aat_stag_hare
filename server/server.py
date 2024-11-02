
import websockets
import asyncio
import pygame

import pygame
import sys
import time
from pygame import K_ESCAPE
from gui import player
import enemy
from agents.random_agent import *
from agents.human import *
from environment.world import StagHare
#from agents.alegaatr import AlegAATr
#from agents.dqn import DQNAgent

pygame.init()
BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)
HUMAN_PLAYERS = 1 # how many human players (clients) we are expecting
AGENTS = 1 # how many agents we are going to add

PAUSE_TIME = 3
HEIGHT = 10
WIDTH = 10

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.


async def handler(websocket, path):

    # does this side need a serve rrunning no but it will make debugging easier in th emean time.

    stag = enemy.Enemy("stag", HEIGHT, WIDTH) # initalizes my enemies for me (the sprites anyway
    hare = enemy.Enemy("hare", HEIGHT, WIDTH)

    while True: # gets us around the "they spawn in the correct position case"
        stag_hare  = StagHare(HEIGHT, WIDTH, hunters)
        if not stag_hare.is_over():
            break

    while True:
        message = await websocket.recv()
        print(f"received message from client: {message}")
        await websocket.send("Game state update")


if __name__ == '__main__':
    hunters = [] # creates our function and our staghunt game

    for i in range(AGENTS):
        hunters.append(Random(name="R" + str(i)))
    for i in range(HUMAN_PLAYERS):
        hunters.append(humanAgent(name="H" + str(i)))  # that should correspond to the clientID hopefully.

    pygame.init()  # actually starts the game.
    start_server = websockets.serve(handler, "localhost", 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()




def draw_grid(height, width): # draws the grid on every frame just so we have it.
    SCREEN.fill(WHITECOLOR)
    widthOffset = (SCREEN_WIDTH / width)
    heightOffset = (SCREEN_HEIGHT / height)
    for x in range(0, width):
        for y in range(0, height):
            rect = pygame.Rect(x*widthOffset, y*heightOffset, widthOffset, heightOffset)
            pygame.draw.rect(SCREEN, BLACKCOLOR, rect, 1)