import websockets
import asyncio
import pygame

connected_clients = {}
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

hunters = []
our_agents = []


# Creating WebSocket server
async def ws_server(websocket):
    # we are hard coding the number of players in bc I honestly can't be bothered.
    # also the "client_id" is prolly going to be determined by its position in the list of "clients"


    print("WebSocket: Server Started.")
    stag = enemy.Enemy("stag", HEIGHT, WIDTH)  # initalizes my enemies for me (the sprites anyway
    hare = enemy.Enemy("hare", HEIGHT, WIDTH)

    for i in range(HUMAN_PLAYERS):
        enemy_name = "H" + str(i)
        new_player = enemy.Enemy(enemy_name, HEIGHT, WIDTH)
        hunters.append(humanAgent(name=enemy_name))
        our_agents.append(new_player)

    for i in range(AGENTS):
        enemy_name = "R" + str(i)
        new_enemy = enemy.Enemy(enemy_name, HEIGHT, WIDTH)
        hunters.append(Random(name=enemy_name))
        our_agents.append(new_enemy)

    try:
        while True:
            stag_hare = StagHare(HEIGHT, WIDTH, hunters)
            if not stag_hare.is_over():
                break

            msg = {}
            msg["HEIGHT"] = HEIGHT
            msg["WIDTH"] = WIDTH


            state = stag_hare.state

            for agent in state.agent_positions:
                msg[agent.name] = state.agent_positions[agent]


            client_id = id(websocket)
            connected_clients[client_id] = websocket
            # Receiving values from client

            msg["CLIENT_ID"] = client_id

            input = await websocket.recv()

            # Prompt message when any of the field is missing

            # Printing details received by client
            print(f"Details Received from Client: {client_id} : {input}")

            print(f"Age: {input}")

            # for agent in state.agent_positions:
            #     pass

            # new_dict_to_send = (f"height: {HEIGHT}, width: {WIDTH}, "

            # Sending a response back to the client
            if int(input) < 18:
                await websocket.send(f"Sorry!, You can't join the club.")
            else:
                await websocket.send(f"Welcome aboard.")

    except websockets.ConnectionClosedError:
        print("Internal Server Error.")


async def main():
    async with websockets.serve(ws_server, "localhost", 7890):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())