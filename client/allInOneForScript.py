import socket
import json
import pygame

SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.

stag_color = (151, 151, 151)
hare_color = (222, 222, 222)
agent_1_color = (40, 30, 245)
agent_2_color = (135, 135, 245)
player_color = (45, 135, 35)
player_2_color = (39, 194, 21)

pygame.font.init()
font = pygame.font.Font(None, 32) # might need to dynamically allocate the font.
font_color = (0,0,0)


from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)

hare_points = 1
stag_points = 3

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)
client_ID = 0
agents = [] # holds all of the sprites for the various agents.

def start_client():

    global client_ID
    host = '192.168.30.17'  # The server's IP address
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
        data = client_socket.recv(65535)
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
          # try to get things to draw to the screen IG>

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
        new_agent = Enemy(new_name, HEIGHT, WIDTH, my_player)
        agents.append(new_agent)

    for i in range(AI_AGENTS):
        new_name = "R" + str(i+1)
        new_agent = Enemy(new_name, HEIGHT, WIDTH)
        agents.append(new_agent)

    # these ones will remain constant
    stag = Enemy("stag", HEIGHT, WIDTH)
    hare = Enemy("hare", HEIGHT, WIDTH)
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
    if "CLIENT_ID" in msg:
        self_id = msg["CLIENT_ID"]
    if "GAME_OVER" in msg:
        if "STAG_DEAD" in msg["GAME_OVER"] and msg["GAME_OVER"]["STAG_DEAD"]:
            stag_dead = msg["GAME_OVER"]["STAG_DEAD"]
        if "HARE_DEAD" in msg["GAME_OVER"] and msg["GAME_OVER"]["HARE_DEAD"]:
            hare_dead = msg["GAME_OVER"]["HARE_DEAD"]

    if "AGENT_POSITIONS" in msg:
        agents_positions = msg["AGENT_POSITIONS"]
        #calculate_points(msg["POINTS"], agents)
        for agent in agents:
            row = agents_positions[agent.name]["Y_COORD"]
            col = agents_positions[agent.name]["X_COORD"]
            new_tuple = row, col
            if agent.name == "stag":
                agent.update(SCREEN, new_tuple, stag_dead)
            if agent.name == "hare":
                agent.update(SCREEN, new_tuple, hare_dead)
            else:
                agent.update(SCREEN, new_tuple)
            agent.update_points(SCREEN, new_tuple)
        draw_round(msg["CURR_ROUND"])

    if "GAME_ENDED" in msg:
        draw_game_over()

    pygame.display.update()

def calculate_points(big_dict, agents):
    for i in range(3): # all possible players
        agents[i].resetPoints()
    for currRound in range(1, len(big_dict["H1"])+1): # if we ever don't have a player this will blow up
        peopleWhoKilledHares = 0
        agents_who_get_points = []
        for i in range(3): # hare points first per round
            if big_dict[agents[i].name][str(currRound)]["hare"] == True:
                agents_who_get_points.append(agents[i])
                peopleWhoKilledHares += 1
        if peopleWhoKilledHares > 0: # otherwise we get a divide by zewro error
            points_that_everyone_gets = hare_points / peopleWhoKilledHares
            for agent in agents_who_get_points:
                agent.setPoints(points_that_everyone_gets)

        if big_dict["H1"][str(currRound)]["stag"] == True: # if at least one player killed a stag (stag points easy)
            for agent in agents:
                agent.setPoints(stag_points)



def draw_grid(height, width): # draws the grid on every frame just so we have it.
    SCREEN.fill(WHITECOLOR)
    widthOffset = (SCREEN_WIDTH / width)
    heightOffset = (SCREEN_HEIGHT / height)
    for x in range(0, width):
        for y in range(0, height):
            rect = pygame.Rect(x*widthOffset, y*heightOffset, widthOffset, heightOffset)
            pygame.draw.rect(SCREEN, BLACKCOLOR, rect, 1)


def draw_round(current_points_dict):
    txt_surf = font.render("Round : " + str(current_points_dict), True, font_color)
    SCREEN.blit(txt_surf, [0,0])

def draw_game_over():
    txt_surf = font.render("Game over!", True, font_color)
    SCREEN.blit(txt_surf, [350, 350])

class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, height, width, my_player=False):
        super(Enemy, self).__init__()
        self.row_to_return, self.col_to_return = None, None # for ethans code
        square_height = SCREEN_HEIGHT / height
        square_width = SCREEN_WIDTH / width
        self.name = name
        self.surf = pygame.surface.Surface((square_height, square_width))
        self.height, self.width = height, width
        self.square_height = self.height
        self.square_width = self.width
        self.points = 0

        if name == "stag":
            self.surf.fill(stag_color)
        elif name == "hare":
            self.surf.fill(hare_color)
        elif name == "R1":
            self.surf.fill(agent_1_color)
        elif name == "R2":
            self.surf.fill(agent_2_color)

        if name[0] == "H":
            if my_player:
                self.surf.fill(player_color)
            else:
                self.surf.fill(player_2_color)


        self.rect = self.surf.get_rect()

    def setPoints(self, newPoints):
        self.points += newPoints

    def resetPoints(self):
        self.points = 0


    def update(self, screen, array_position, dead=False):
        # here
        new_position = calculate_position(self, array_position)
        if dead:
            self.surf.fill((200, 60, 20))
            screen.blit(self.surf, new_position)
        else:
            self.update_alive()
            screen.blit(self.surf, new_position) # so this one works.

    def update_alive(self):
        if self.name == "stag":
            self.surf.fill(stag_color)
        elif self.name == "hare":
            self.surf.fill(hare_color)



    def update_points(self, screen, array_position):
        if not self.name[0] == "H" and not self.name[0] == "R":  # should filter out all non agents.
            return

        new_position = calculate_position(self, array_position)
        txt_surf = font.render(str(self.points), True, font_color)
        screen.blit(txt_surf, new_position)

        # create the new font here make sure all the changes work so far tho.


def calculate_position(self, array_position):
    current_x = array_position[0]
    current_y = array_position[1]
    current_x = current_x * (SCREEN_WIDTH / self.width)
    current_y = current_y * (SCREEN_HEIGHT / self.height)
    return current_y, current_x


def set_next_action(self, new_row, new_col) -> None:
    self.row_to_return, self.col_to_return = new_row, new_col







if __name__ == "__main__":
    start_client()