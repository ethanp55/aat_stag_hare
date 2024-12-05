import socket

import json
from server import enemy
import pygame

SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.

from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)
stag_points = 3
hare_points = 1

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)
client_ID = 0
agents = [] # holds all of the sprites for the various agents.

def start_client():

    global client_ID
    host = '127.0.0.1'  # The server's IP address
    port = 12345         # The port number to connect to
    pygame.init()  # actually starts the game.
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
        try: # get the stuff first
            # Deserialize the JSON response from the server
            server_response = json.loads(data.decode())

        except json.JSONDecodeError:
            pass

        if server_response != None:

            if "CLIENT_ID" in server_response:
                client_ID = server_response["CLIENT_ID"]
            if "HUMAN_AGENTS" in server_response:
                initalize(server_response)
            print_board(server_response)
        message = {
            "NEW_INPUT" : None,
        }
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pressed_keys = pygame.key.get_pressed()
                print("We TRYING to send a new position")
                message = {
                    "NEW_INPUT" : adjust_position(pressed_keys),
                    "CLIENT_ID": client_ID,
                }

            if event.type == pygame.QUIT:
                pygame.quit()
            break

        client_socket.send(json.dumps(message).encode())  # send a packet on every frame.
        pygame.display.update()  # try to get things to draw to the screen IG>

    # Close the connection
    client_socket.close()


def initalize(server_response):
    global HUMAN_AGENTS, AI_AGENTS, HEIGHT, WIDTH, client_ID
    HUMAN_AGENTS = server_response["HUMAN_AGENTS"]
    AI_AGENTS = server_response["AI_AGENTS"]
    HEIGHT = server_response["HEIGHT"]
    WIDTH = server_response["WIDTH"]

    for i in range(HUMAN_AGENTS):
        new_name = "H" + str(i+1)
        my_player = False
        if str(i+1) == str(client_ID):
            my_player = True
        new_agent = enemy.Enemy(new_name, HEIGHT, WIDTH, my_player)
        agents.append(new_agent)

    for i in range(AI_AGENTS):
        new_name = "R" + str(i+1)
        new_agent = enemy.Enemy(new_name, HEIGHT, WIDTH)
        agents.append(new_agent)

    # these ones will remain constant
    stag = enemy.Enemy("stag", HEIGHT, WIDTH)
    hare = enemy.Enemy("hare", HEIGHT, WIDTH)
    agents.append(stag)
    agents.append(hare)


def adjust_position(pressed_keys):
    curr_row = 0
    curr_col = 0
    if pressed_keys[K_UP]:
        curr_row -= 1
    if pressed_keys[K_DOWN]:
        curr_row += 1  # move down
    if pressed_keys[K_LEFT]:
        curr_col -= 1  # move left
    if pressed_keys[K_RIGHT]:
        curr_col += 1  # move right
    return curr_row, curr_col

def print_board(msg):
    stag_dead = False
    hare_dead = False
    if HEIGHT is not None or WIDTH is not None:
        draw_grid(HEIGHT, WIDTH) # draw the board first
    points = 0
    if "CLIENT_ID" in msg:
        self_id = msg["CLIENT_ID"]
    if "AGENT_POSITIONS" in msg:
        agents_positions = msg["AGENT_POSITIONS"]
        if "GAME_OVER" in msg:
            stag_dead = msg["GAME_OVER"]["STAG_DEAD"]
            hare_dead = msg["GAME_OVER"]["HARE_DEAD"]
        for agent in agents:
            points = calculate_points(msg["POINTS"], agent.name)
            row = agents_positions[agent.name]["Y_COORD"]
            col = agents_positions[agent.name]["X_COORD"]
            new_tuple = row, col

            if agent.name == "stag":
                agent.update(SCREEN, new_tuple, stag_dead)
            elif agent.name == "hare":
                agent.update(SCREEN, new_tuple, hare_dead)
            else:
                agent.update(SCREEN, new_tuple)
                agent.update_points(SCREEN, new_tuple, points)
    pygame.display.update()

def calculate_points(big_dict, agent_name):
    points = 0
    for key in big_dict.keys():
        if key == agent_name:
            for round in big_dict[key]:
                if big_dict[key][round]["stag"] == True:
                    points = points + stag_points
                if big_dict[key][round]["hare"] == True:
                    points = points + hare_points

    return points




def draw_grid(height, width): # draws the grid on every frame just so we have it.
    SCREEN.fill(WHITECOLOR)
    widthOffset = (SCREEN_WIDTH / width)
    heightOffset = (SCREEN_HEIGHT / height)
    for x in range(0, width):
        for y in range(0, height):
            rect = pygame.Rect(x*widthOffset, y*heightOffset, widthOffset, heightOffset)
            pygame.draw.rect(SCREEN, BLACKCOLOR, rect, 1)

if __name__ == "__main__":
    start_client()