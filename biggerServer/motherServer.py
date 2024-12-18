# this fetcher just holds connections and instantiates game servers when we have enough people, think 12. do NOT hold all connections, delete them after passign them down to gameServer

import json
import socket
import copy

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

from agents.random_agent import *
from agents.human import *
from environment.world import StagHare
from server import enemy
from gameServer import GameServer
import gameServer


# NOTE: the human + AI agents must always add up to 3. has to do with the way stag_hare is configured.
HUMAN_PLAYERS = 1 # how many human players (clients) we are expecting
AI_AGENTS = 2 # how many agents we are going to add

#from agents.alegaatr import AlegAATr
#from agents.dqn import DQNAgent

PAUSE_TIME = 3

connected_clients = {}
client_input = {}
client_usernames = {}
HEIGHT = 3 # leave this hardcoded for now.
WIDTH = 3
client_id_dict = {}
hunters = []
MAX_ROUNDS = 2
round = 1

HARE_POINTS = 10
STAG_POINTS = 20
# these ones always stay the same
stag = enemy.Enemy("stag", HEIGHT, WIDTH)
hare = enemy.Enemy("hare", HEIGHT, WIDTH)

def start_server(host='192.168.30.17', port=12345):

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(12)  # Allow only one connection

    print(f"Server listening on {host}:{port}...")

    while True: # just keeps running and listening for clients, capable of running multiple servers.
        client_socket, client_address = server_socket.accept()
        connected_clients[len(connected_clients)] = client_socket
        client_id_dict[client_socket] = len(connected_clients)

        data = client_socket.recv(1024)

        try:
            # Deserialize the JSON data
            received_json = json.loads(data.decode())
            print(f"Received JSON from client: {received_json}")
            client_usernames[len(connected_clients)] = received_json["USERNAME"]


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
            # passes down the new player list, calls that object (so we should now be cooking) and then clears out the stuff. Do I need to make threads?
            new_player_list = copy.copy(connected_clients)
            GameServer(new_player_list, client_id_dict, client_usernames)
            connected_clients.clear()
            client_id_dict.clear()
            client_usernames.clear()


if __name__ == "__main__":
    start_server()
