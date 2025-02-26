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


# NOTE
HUMAN_PLAYERS = 1 # how many human players (clients) we are expecting (This should be 12 for the full study)

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
# your workstation ip is '192.168.30.17', use local host while at home
def start_server(host='10.55.10.103', port=12345):

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(12)  # Allow only one connection

    while True: # just keeps running and listening for clients, capable of running multiple servers.
        client_socket, client_address = server_socket.accept()
        connected_clients[len(connected_clients)] = client_socket
        client_id_dict[client_socket] = len(connected_clients)

        data = client_socket.recv(1024)

        try:
            # Deserialize the JSON data
            received_json = json.loads(data.decode())
            client_usernames[len(connected_clients)] = received_json["USERNAME"]


            # Create a response
            response = {
                "message": "Hello from the server!",
                "HEIGHT": HEIGHT,
                "WIDTH": WIDTH,
                "CLIENT_ID" : client_id_dict[client_socket],
            }
            # Serialize and send the response as JSON
            client_socket.send(json.dumps(response).encode())
        except json.JSONDecodeError:
            pass # don't do anything but still handle the exception

        if len(connected_clients) == HUMAN_PLAYERS: # when we have all the players that we are expecting
            # passes down the new player list, calls that object (so we should now be cooking) and then clears out the stuff. Do I need to make threads?
            new_player_list = copy.copy(connected_clients)
            GameServer(new_player_list, client_id_dict, client_usernames)
            connected_clients.clear()
            client_id_dict.clear()
            client_usernames.clear()


if __name__ == "__main__":
    start_server()
