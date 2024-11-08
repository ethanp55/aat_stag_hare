import json
import socket
import websockets
import asyncio
import pygame
from websockets.sync.client import connect

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

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

ALL_READY = pygame.USEREVENT + 1
ALL_READY_EVENT = pygame.event.Event(ALL_READY)

#from agents.alegaatr import AlegAATr
#from agents.dqn import DQNAgent

PAUSE_TIME = 3
HEIGHT = 10
WIDTH = 10

SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800

connected_clients = {}
client_input = {}
HEIGHT = 10
WIDTH = 10

global stag_hare
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.

# Set up the server to listen on a specific host and port
def start_server():
    host = '127.0.0.1'  # Localhost
    port = 12345  # Port to bind the server

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # Allow only one connection

    print(f"Server listening on {host}:{port}...")

    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    connected_clients[len(connected_clients)] = client_socket

    # Receive data from the client
    data = client_socket.recv(1024)

    try:
        # Deserialize the JSON data
        received_json = json.loads(data.decode())
        print(f"Received JSON from client: {received_json}")

        # Create a response
        response = {
            "message": "Hello from the server!",
            "status": "success",
            "client_data": received_json
        }

        # Serialize and send the response as JSON
        client_socket.send(json.dumps(response).encode())
    except json.JSONDecodeError:
        print("Received data is not valid JSON.")
        client_socket.send(json.dumps({"error": "Invalid JSON format"}).encode())



    stag_hunt_game_loop(connected_clients)
    # Close the connection
    client_socket.close()



def stag_hunt_game_loop(connected_clients):

    hunters = []  # first things first initalize the hunters and get them ready
    for i in range(HUMAN_PLAYERS):
        new_name = "H" + str(i+1)
        hunters.append(humanAgent(name=new_name))
    for i in range(AGENTS):
        new_name = "R" + str(i+1)
        hunters.append(Random(name=new_name))

    while True:  # set up stag hunt and avoid weird edgecase
        stag_hare = StagHare(HEIGHT, WIDTH, hunters)
        if not stag_hare.is_over():
            break

    this_player = player.Player("player", HEIGHT, WIDTH)
    stag = enemy.Enemy("stag", HEIGHT, WIDTH)
    hare = enemy.Enemy("hare", HEIGHT, WIDTH)
    agent1 = enemy.Enemy("agent1", HEIGHT, WIDTH)
    agent2 = enemy.Enemy("agent2", HEIGHT, WIDTH)

    pygame.init()  # actually starts the game.
    running = True
    rewards = [0] * (len(hunters) + 2)

    # if the thing is full, run this
    # pygame.event.post(ALL_READY_EVENT)

    while True:
        stag_hare = StagHare(HEIGHT, WIDTH, hunters)
        if not stag_hare.is_over():
            break



    while True:

        for client in connected_clients:



            while running:  #and not stag_hare.is_over(): # make sure that we aren't over
                response = {
                    "HEIGHT" : HEIGHT,
                    "WIDTH" : WIDTH,
                    "CLIENT_ID" : client
                }
                connected_clients[client].send(json.dumps(response).encode())




                draw_grid(HEIGHT, WIDTH)

                state = stag_hare.return_state()

                for agent in stag_hare.state.agent_positions: # go ahead and print this out every rfame
                    if agent == 'hare':
                        hare.update(SCREEN, stag_hare.state.agent_positions[agent])
                    if agent == "stag":
                        stag.update(SCREEN, stag_hare.state.agent_positions[agent])
                    if agent == "R1":
                        agent1.update(SCREEN, stag_hare.state.agent_positions[agent])
                    if agent == "R2":
                        agent2.update(SCREEN, stag_hare.state.agent_positions[agent])
                    if agent == "H":
                        # current_position = (3,2)
                        # this_player.update(SCREEN, current_position)
                        this_player.update(SCREEN, stag_hare.state.agent_positions[agent])



                # for event in pygame.event.get():
                #
                #     if event.type == pygame.QUIT:
                #         running = False
                #
                #     if event.type == ALL_READY:
                #         pressed_keys = pygame.key.get_pressed()
                #
                #         #new_row, new_col = set_player_position(pressed_keys, state)
                #         #hunters[-1].set_next_action(new_row, new_col)
                #
                #         round_rewards = stag_hare.transition()
                #
                #         # Update rewards
                #         for i, reward in enumerate(round_rewards):
                #             rewards[i] += reward





                pygame.display.update()

                    # if event.type == pygame.KEYDOWN:
                    #     if event.key == K_ESCAPE:  # gives us a way to stop execution.
                    #         running = False

                if stag_hare.is_over():
                    if stag_hare.state.hare_captured():
                        hare.update(SCREEN, state.agent_positions["hare"], True)
                    else:
                        stag.update(SCREEN, state.agent_positions["stag"], True)
                    pygame.display.update()
                    time.sleep(PAUSE_TIME)
                    running = False



def draw_grid(height, width): # draws the grid on every frame just so we have it.
    SCREEN.fill(WHITECOLOR)
    widthOffset = (SCREEN_WIDTH / width)
    heightOffset = (SCREEN_HEIGHT / height)
    for x in range(0, width):
        for y in range(0, height):
            rect = pygame.Rect(x*widthOffset, y*heightOffset, widthOffset, heightOffset)
            pygame.draw.rect(SCREEN, BLACKCOLOR, rect, 1)



if __name__ == "__main__":
    start_server()