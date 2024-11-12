import json
import socket
import threading

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

import pygame
import sys
import time
from pygame import K_ESCAPE
from agents.random_agent import *
from agents.human import *
from environment.world import StagHare
from server import enemy

HUMAN_PLAYERS = 2 # how many human players (clients) we are expecting
AI_AGENTS = 1 # how many agents we are going to add

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

client_id_dict = {}

hunters = []

# these ones always stay the same
stag = enemy.Enemy("stag", HEIGHT, WIDTH)
hare = enemy.Enemy("hare", HEIGHT, WIDTH)

agents = [] # holds the actual agents that we want to update


global stag_hare
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.

# Set up the server to listen on a specific host and port
def start_server(host='127.0.0.1', port=12345):

    global hunters
    hunters = []  # first things first initalize the hunters and get them ready
    for i in range(HUMAN_PLAYERS):
        new_name = "H" + str(i + 1)
        hunters.append(humanAgent(name=new_name))
        new_agent = enemy.Enemy(new_name, HEIGHT, WIDTH)
        agents.append(new_agent)

    for i in range(AI_AGENTS):
        new_name = "R" + str(i + 1)
        hunters.append(Random(name=new_name))
        new_agent = enemy.Enemy(new_name, HEIGHT, WIDTH)
        agents.append(new_agent)

    while True:  # set up stag hunt and avoid weird edgecase
        stag_hare = StagHare(HEIGHT, WIDTH, hunters)
        if not stag_hare.is_over():
            break

    # these ones will remain constant


    agents.append(stag)
    agents.append(hare)


    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # Allow only one connection

    print(f"Server listening on {host}:{port}...")

    while True:
        client_socket, client_address = server_socket.accept()
        connected_clients[len(connected_clients)] = client_socket
        client_id_dict[client_socket] = len(connected_clients)

        data = client_socket.recv(1024) # beleive its bricking becuase it wants to receive the packet

        try:
            # Deserialize the JSON data
            received_json = json.loads(data.decode())
            print(f"Received JSON from client: {received_json}")

            # Create a response
            response = {
                "message": "Hello from the server!",
                "HUMAN_AGENTS": HUMAN_PLAYERS,
                "AI_AGENTS": AI_AGENTS,
                "HEIGHT": HEIGHT,
                "WIDTH": WIDTH,
            }

            # Serialize and send the response as JSON
            client_socket.send(json.dumps(response).encode())
        except json.JSONDecodeError:
            print("Received data is not valid JSON.")
            client_socket.send(json.dumps({"error": "Invalid JSON format"}).encode())



        threading.Thread(target=handle_client, args=(client_socket,)).start()



def handle_client(client_socket):
    global connected_clients

    try:
        while True:
            if len(connected_clients) == HUMAN_PLAYERS:
                stag_hunt_game_loop()
                break
            else:
                response = {
                    "message": "Hello from the server!",
                    "HUMAN_AGENTS": HUMAN_PLAYERS,
                    "AI_AGENTS": AI_AGENTS,
                    "HEIGHT": HEIGHT,
                    "WIDTH": WIDTH,
                }
                client_socket.send(json.dumps(response).encode())

    except Exception as e:
        print("Error with something")
    finally:
        client_socket.close()

def stag_hunt_game_loop():


    # we need to be smarter about these ones

    pygame.init()  # actually starts the game.
    running = True
    rewards = [0] * (len(hunters) + 2)

    # if the thing is full, run this
    # pygame.event.post(ALL_READY_EVENT)

    while True:
        stag_hare = StagHare(HEIGHT, WIDTH, hunters)
        if not stag_hare.is_over():
            break



    while running:

        for client in connected_clients:
            data = connected_clients[client].recv(1024)
            pass
            if data != None:
                received_json = json.loads(data.decode())
                if "NEW_INPUT" in received_json and received_json["NEW_INPUT"] is not None:
                    print(f"{client} has tried to move!")
                    client_input[client] = received_json["NEW_INPUT"]

                if len(client_input) == len(connected_clients): # everyone has an answer
                    for i in range(HUMAN_PLAYERS):
                        for agent in agents:
                            check_name = "H" + str(i+1)
                            if agent.name == check_name:
                                 next_round(stag_hare, rewards, client_input)
                                 client_input.clear()

            current_state = {}

            for agent in stag_hare.state.agent_positions:
                hidden_second_dict = {}
                hidden_second_dict["X_COORD"] = int(stag_hare.state.agent_positions[agent][1])
                hidden_second_dict["Y_COORD"] = int(stag_hare.state.agent_positions[agent][0])
                current_state[agent] = hidden_second_dict



            response = {
                "CLIENT_ID": client,
                "AGENT_POSITIONS": current_state,
            }
            new_message = json.dumps(response).encode()
            connected_clients[client].send(new_message)




            draw_grid(HEIGHT, WIDTH)

            state = stag_hare.return_state()

            # for agent in stag_hare.state.agent_positions: # go ahead and print this out every rfame
            #     if agent == 'hare':
            #         hare.update(SCREEN, stag_hare.state.agent_positions[agent])
            #     if agent == "stag":
            #         stag.update(SCREEN, stag_hare.state.agent_positions[agent])

            for agent in agents: # that should be all we need to do actually, throw them in an array and let it do everything else.
                agent.update(SCREEN, stag_hare.state.agent_positions[agent.name])




            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

            #pygame.display.update()

                # if event.type == pygame.KEYDOWN:
                #     if event.key == K_ESCAPE:  # gives us a way to stop execution.
                #         running = False

            if stag_hare.is_over():
                if stag_hare.state.hare_captured():
                    hare.update(SCREEN, state.agent_positions["hare"], True)
                else:
                    stag.update(SCREEN, state.agent_positions["stag"], True)
                #pygame.display.update()
                print("GAME OVER")
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


def next_round(stag_hare, rewards, new_positions):

    for client_id in new_positions:
        client_agent = "H" + str(client_id + 1)
        current_position = stag_hare.state.agent_positions[client_agent]
        new_tuple_row = new_positions[client_id][0] + current_position[0]
        new_tuple_col = new_positions[client_id][1] + current_position[1]
        hunters[client_id].set_next_action(new_tuple_row, new_tuple_col)

                 # no clue if this will work lol.

        print(f"this is the client_ID, {client_id}")


    round_rewards = stag_hare.transition()
    #
    # Update rewards
    for i, reward in enumerate(round_rewards):
        rewards[i] += reward


if __name__ == "__main__":
    start_server()