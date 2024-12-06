import json
import socket
import threading
from cgitb import small

import select
from numpy.f2py.crackfortran import true_intent_list

from server.timer import Timer

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

import pygame
import sys
import time
from server import timer
from pygame import K_ESCAPE
from agents.random_agent import *
from agents.human import *
from environment.world import StagHare
from server import enemy

import multiprocessing

HUMAN_PLAYERS = 2 # how many human players (clients) we are expecting
AI_AGENTS = 1 # how many agents we are going to add

ALL_READY = pygame.USEREVENT + 1
ALL_READY_EVENT = pygame.event.Event(ALL_READY)

#from agents.alegaatr import AlegAATr
#from agents.dqn import DQNAgent

PAUSE_TIME = 3
SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800
connected_clients = {}
client_input = {}
HEIGHT = 10
WIDTH = 10
client_id_dict = {}
hunters = []
MAX_ROUNDS = 2
round = 1

HARE_POINTS = 1 / HUMAN_PLAYERS # multi threading work around
STAG_POINTS = 3 / HUMAN_PLAYERS
# these ones always stay the same
stag = enemy.Enemy("stag", HEIGHT, WIDTH)
hare = enemy.Enemy("hare", HEIGHT, WIDTH)

from queue import Queue

agents = [] # holds the actual agents that we want to update
stag_hare = None
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.

# Set up the server to listen on a specific host and port
def start_server(host='192.168.30.17', port=12345):
    global stag_hare
    global hunters
    manager = multiprocessing.Manager()
    player_points = manager.dict()

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

    player_points = player_points_initialization(MAX_ROUNDS, player_points, hunters)

    agents.append(stag)
    agents.append(hare)

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # Allow only one connection

    print(f"Server listening on {host}:{port}...")

    while True: # this here is our wihle true loop, needs to break when we have enough clients
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
                "CLIENT_ID" : client_id_dict[client_socket],
            }
            # Serialize and send the response as JSON
            client_socket.send(json.dumps(response).encode())
        except json.JSONDecodeError:
            print("Received data is not valid JSON.")
            client_socket.send(json.dumps({"error": "Invalid JSON format"}).encode())

        if len(connected_clients) == HUMAN_PLAYERS:
            break

    main_game_loop(player_points)


def main_game_loop(player_points):
    global client_id_dict
    while True:
        client_input = {}
        while True:
            send_state(player_points) # sends out the current game state
            data = get_client_data()
            for client, received_json in data.items():
                if "NEW_INPUT" in received_json and received_json["NEW_INPUT"] != None:
                    client_input[client_id_dict[client]] = received_json["NEW_INPUT"]
                    print(f"Received input from {client}: {received_json['NEW_INPUT']}")
            # Check if all clients have provided input
            if len(client_input) == len(connected_clients):
                break
        print("All clients have provided input. continuing")

        running = stag_hunt_game_loop(player_points, client_input)
        if running == False:
            break
        client_input.clear()



def handle_client(client, input_queue):
    try:
        data = connected_clients[client].recv(1024)
        if data:
            try:
                received_json = json.loads(data.decode())
                if "NEW_INPUT" in received_json and received_json["NEW_INPUT"] is not None:
                    input_data = {client: received_json["NEW_INPUT"]}
                    input_queue.put(input_data)  # Push the input into the queue
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"Error with client {client}: {e}")


def stag_hunt_game_loop(player_points, player_input):

    global connected_clients, round
    global stag_hare
    pygame.init()  # Initialize pygame
    rewards = [0] * (len(hunters) + 2)

    next_round(stag_hare, rewards, player_input)

    send_state(player_points)

    draw_grid(HEIGHT, WIDTH)
    state = stag_hare.return_state()

    for agent in agents:
        agent.update(SCREEN, stag_hare.state.agent_positions[agent.name])

    if stag_hare.is_over():
        timer = Timer(2)
        hare_dead = False
        stag_dead = False
        while True:

            print("*************GAME OVER************")
            print("HERE Are the current playre points" , player_points)

            if stag_hare.state.hare_captured():
                find_hunter_hare(player_points, round)
                hare.update(SCREEN, state.agent_positions["hare"], True)
                hare_dead = True
            else:
                find_hunter_stag(player_points, round)
                stag.update(SCREEN, state.agent_positions["stag"], True)
                stag_dead = True

            print("here are the post player points", player_points)
            small_dict = {}  # helps me know who to light up red on death.
            small_dict["HARE_DEAD"] = hare_dead
            small_dict["STAG_DEAD"] = stag_dead

            points_to_send = dict(player_points)
            pygame.display.update()
            current_state = create_current_state()
            for client in connected_clients: # does this update the points correctly?
                client_id = client_id_dict[connected_clients[client]]
                response = {
                    "CLIENT_ID": client_id,
                    "AGENT_POSITIONS": current_state,
                    "POINTS": dict(points_to_send),
                    "GAME_OVER" : small_dict,
                }

                new_message = json.dumps(response).encode()
                connected_clients[client].send(new_message)

            if timer.time_out():
                break

        pygame.display.update()
        time.sleep(PAUSE_TIME)
        if round == MAX_ROUNDS:
            print("GAME OVER")
            return False
        else:
            round += 1
            reset_stag_hare()


def send_state(player_points):
    global stag_hare
    current_state = create_current_state()

    global connected_clients
    send_player_points = player_points.copy()
    for client in connected_clients:
        client_id = client_id_dict[connected_clients[client]]
        response = {
            "CLIENT_ID": client_id,
            "AGENT_POSITIONS": current_state,
            "POINTS": send_player_points
        }

        new_message = json.dumps(response).encode()
        connected_clients[client].send(new_message)


def create_current_state():
    current_state = {}

    # Prepare current state to send to clients
    for agent in stag_hare.state.agent_positions:
        hidden_second_dict = {}
        hidden_second_dict["X_COORD"] = int(stag_hare.state.agent_positions[agent][1])
        hidden_second_dict["Y_COORD"] = int(stag_hare.state.agent_positions[agent][0])
        current_state[agent] = hidden_second_dict
    return current_state


def worker2(dictionary, hunter_name, round, updated_states_dict):
    print("updated states dict ", updated_states_dict)

    if hunter_name not in dictionary:
        # If the hunter doesn't exist in the dictionary, create an entry for them
        dictionary[hunter_name] = {}

    current_entry = dictionary[hunter_name]

    # If the round doesn't exist, create a new entry for that round
    if round not in current_entry:
        current_entry[round] = {}

    # Check if "hare" is in the updated states dict and add it if necessary
    if "hare" in updated_states_dict:
        current_entry[round]["hare"] = updated_states_dict["hare"]

    # Check if "stag" is in the updated states dict and add it if necessary
    if "stag" in updated_states_dict:
        current_entry[round]["stag"] = updated_states_dict["stag"]

    # After updating the round, save it back to the dictionary
    dictionary[hunter_name] = current_entry

    print("post update states dict ", dictionary)


def player_points_initialization(MAX_ROUNDS, player_points, hunters):
    for hunter in hunters:
        if hunter.name not in player_points:
            player_points[hunter.name] = {}  # Initialize an empty dictionary for each hunter (not a list)

        for round in range(1, MAX_ROUNDS+1):
            # Directly create the round entry with "stag" and "hare" for each hunter
            current_entry = player_points[hunter.name]

            small_dict = {
                "stag": False,
                "hare": False,
            }
            # Directly assign the round as a key and small_dict as the value
            current_entry[round] = small_dict
            if round not in player_points[hunter.name]:
                player_points[hunter.name] = current_entry
    return player_points



def reset_stag_hare():
    global stag_hare
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

    agents.append(stag)
    agents.append(hare)


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
        client_agent = "H" + str(client_id)
        current_position = stag_hare.state.agent_positions[client_agent]
        new_tuple_row = new_positions[client_id][0] + current_position[0]
        new_tuple_col = new_positions[client_id][1] + current_position[1]
        hunters[client_id-1].set_next_action(new_tuple_row, new_tuple_col)
        print(f"this is the client_ID, {client_id}")

    round_rewards = stag_hare.transition()
    for i, reward in enumerate(round_rewards):
        rewards[i] += reward

def get_client_data():
    ready_to_read, _, _ = select.select(list(connected_clients.values()), [], [], 0.1)
    data = {}
    for client in ready_to_read:
        try:
            msg = ''
            while True:  # Accumulate data until the full message is received
                chunk = client.recv(1024).decode()
                msg += chunk
                if len(chunk) < 1024:  # End of message
                    break
            if msg:
                data[client] = json.loads(msg)
        except Exception as e:
            pass
    return data


def find_hunter_hare(player_points, round):
    global stag_hare, HARE_POINTS
    print("distributing points")
    hare_position = stag_hare.state.agent_positions["hare"]
    hare_positionX = hare_position[1]
    hare_positionY = hare_position[0]
    # we need the hare here.
    print("here is the hare position", hare_positionY, ",", hare_positionX)
    for hunter in stag_hare.state.agent_positions:
        if not hunter[0] == "H" and not hunter[0] == "R":  # should filter out all non agents.
            continue

        position = stag_hare.state.agent_positions[hunter]
        positionX = position[1]
        positionY = position[0]
        print("here is the position of the agent that we think ", positionY, ",", positionX)

        if abs(positionX - hare_positionX) == 1 and positionY == hare_positionY or \
                abs(positionY - hare_positionY) == 1 and positionX == hare_positionX: # if they are right next to eachtoher
            small_dict = {}
            small_dict["hare"] = True
            print("Hunter ", hunter, " was given hare points! next to eachtoher no diff")
            worker2(player_points, hunter, round, small_dict)

        elif positionX == hare_positionX and (
                (positionY == 0 and hare_positionY == HEIGHT - 1) or
                (positionY == HEIGHT - 1 and hare_positionY == 0)
        ): # seperated by height
            small_dict = {}
            small_dict["hare"] = True
            print("Hunter ", hunter, " was given hare points! shot around wall left or right")
            worker2(player_points, hunter, round, small_dict)

        elif positionY == hare_positionY and (
                (positionX == 0 and hare_positionX == WIDTH - 1) or
                (positionX == WIDTH - 1 and hare_positionX == 0)
        ): # seperated by width
            small_dict = {}
            small_dict["hare"] = True
            print("Hunter ", hunter, " was given hare points! shot thorugh celing or floor")
            worker2(player_points, hunter, round, small_dict)


# given that we already know that the stag is dead, all players receive points. Much easier than hare.f
def find_hunter_stag(player_points, round):
    print("distributing points")
    global hunters, STAG_POINTS
    for hunter in stag_hare.state.agent_positions:
        if not hunter[0] == "H" and not hunter[0] == "R":  # should filter out all non agents.
            continue

        small_dict = {}
        small_dict["stag"] = True

        worker2(player_points, hunter, round, small_dict)
        print("Hunter ", hunter, " was given stag points!")

def add_player_points(player_points):
    pass


if __name__ == "__main__":
    start_server()