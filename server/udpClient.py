import socket

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
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.





from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)



SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

HEIGHT = 0
WIDTH = 0

def start_client():
    host = '127.0.0.1'  # The server's IP address
    port = 12345         # The port number to connect to

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((host, port))

    # Send data to the server
    message = {
        "message" : "Hello from the client!"
    }
    client_socket.send(json.dumps(message).encode())

    # Receive a response from the server
    while True:
        server_response = None
        data = client_socket.recv(1024)
        try:
            # Deserialize the JSON response from the server
            server_response = json.loads(data.decode())
            print(f"Received JSON from server: {server_response}")
        except json.JSONDecodeError:
            pass


        if server_response != None:

            Height = 0
            Width = 0
            self_ID = None
            print_board(server_response)


    # Close the connection
    client_socket.close()



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
    # if height is not None or width is not None:
    #     draw_grid(height, width)


if __name__ == "__main__":
    start_client()