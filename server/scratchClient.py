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
            if "SElF_ID" in real_msg:
                self_id = real_msg["SELF_ID"]
            pygame.display.update()




            pressed_keys = pygame.key.get_pressed()
            if len(pressed_keys) == 1:

                position_update = set_player_position(pressed_keys)
                print("this is the position update ", position_update)
                #await ws.send(json.dumps(position_update))



                    #new_row, new_col = set_player_position(pressed_keys, state)


                # for agent in msg["agents"]:
                #     if agent == 'hare':
                #         hare.update(SCREEN, state.agent_positions[agent])
                #     if agent == "stag":
                #         stag.update(SCREEN, state.agent_positions[agent])
                #     if agent == "R1":
                #         agent1.update(SCREEN, state.agent_positions[agent])
                #     if agent == "R2":
                #         agent2.update(SCREEN, state.agent_positions[agent])
                #     if agent == "H":
                #         # current_position = (3,2)
                #         # this_player.update(SCREEN, current_position)
                #         this_player.update(SCREEN, state.agent_positions[agent])



                # if event.type == pygame.KEYDOWN:
                #     if event.key == K_ESCAPE:  # gives us a way to stop execution.
                #         running = False



def print_board(msg):
    height = None
    width = None
    self_id = None
    if "HEIGHT" in msg:
        height = msg["HEIGHT"]
    if "WIDTH" in msg:
        width = msg["WIDTH"]
    if "SELF_ID" in msg:
        self_id = msg["SELF_ID"]
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



def set_player_position(pressed_keys):

    curr_row, curr_col = 0,0# because thats the name of the human player
    if pressed_keys[K_UP]:
        curr_row -= 1
    if pressed_keys[K_DOWN]:
        curr_row += 1  # move down
    if pressed_keys[K_LEFT]:
        curr_col -= 1  # move left
    if pressed_keys[K_RIGHT]:
        curr_col += 1  # move right

    print("we have updated the player position")
    return curr_row, curr_col


if __name__ == "__main__":
    asyncio.run(ws_client())
