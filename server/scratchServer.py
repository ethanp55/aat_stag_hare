import json

import websockets
import asyncio
import pygame


import pygame
import sys
import time
from pygame import K_ESCAPE
from gui import player
from gui import enemy
from agents.random_agent import *
from agents.human import *
from environment.world import StagHare
HUMAN_PLAYERS = 1 # how many human players (clients) we are expecting
AGENTS = 2 # how many agents we are going to add


#from agents.alegaatr import AlegAATr
#from agents.dqn import DQNAgent

PAUSE_TIME = 3
HEIGHT = 10
WIDTH = 10


connected_clients = {}
client_input = {}
HEIGHT = 10
WIDTH = 10

global stag_hare

# Creating WebSocket server
async def ws_server(websocket, path):
    client_id = id(websocket)
    connected_clients[client_id] = websocket


    try:
        # Handle first message
        input_data = await websocket.recv()
        print(f"Details Received from Client: {client_id} : {input_data}")
        print(f"Age: {input_data}")
        long_client_id = id(websocket)
        client_id = connected_clients.__sizeof__() + 1
        connected_clients[client_id] = websocket
        response = {}
        await websocket.send(json.dumps(response))

        # Keep connection open
        while True:
            response["HEIGHT"] = HEIGHT
            response["WIDTH"] = WIDTH
            response["SELF_ID"] = client_id


           # for agent in stag_hare.state.agent_positions:
             #   response[str(agent.name)] = stag_hare.state.agent_positions[agent]

            await websocket.send(json.dumps(response))
            # Wait for future messages
            input_data = await websocket.recv()
            print(f"Received another message: {input_data}")
            client_input[client_id] = input_data
            # Optionally, process additional messages here

    except websockets.ConnectionClosed as e:
        print(f"Connection with client {client_id} closed: {e}")


async def main():
    hunters = [] # first things first initalize the hunters and get them ready
    for i in range(HUMAN_PLAYERS):
        new_name = "H" + str(i)
        hunters.append(humanAgent(name=new_name))
    for i in range(AGENTS):
        new_name = "R" + str(i)
        hunters.append(Random(name=new_name))

    while True: # set up stag hunt and avoid weird edgecase
        stag_hare = StagHare(HEIGHT, WIDTH, hunters)
        if not stag_hare.is_over():
            break

    # start the actual server and go from there
    async with websockets.serve(ws_server, "localhost", 7890):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
