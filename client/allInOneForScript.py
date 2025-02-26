import socket
import json
import pygame
import pygame_widgets
from pygame_widgets.button import Button


SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.
import time

pygame.init()  # actually starts the game.
font = pygame.font.Font(None, 32) # might need to dynamically allocate the font.
font_color = (0,0,0)
leaderboard_font = pygame.font.Font(None, 64)
leaderboard_font_color = (0,0,0)

stag_button = Button(
    SCREEN, 700, 700, 30, 30, text="stag",
    fontSize=30, margin=20,
    inactiveColour=(135, 126, 126),
    pressedColour=(0,255,0), radius=20,
    onClick=lambda: set_active_button("stag")
)

hare_button = Button(
    SCREEN, 700, 750, 30, 30, text="hare",
    fontSize=30, margin=20,
    inactiveColour=(135, 126, 126),
    pressedColour=(0,255,0), radius=20,
    onClick=lambda: set_active_button("hare")
)

active_button = "hare" # WHEEE
buttons_active = True


# self.surf.fill = hare_sprite thats how you could do it if you wanted to use color tiles instead of sprites.

stag_sprite = pygame.image.load("stag.png")
hare_sprite = pygame.image.load("hare.png")
my_hunter = pygame.image.load("my_hunter.png")
other_hunter = pygame.image.load("other_hunter.png")

#stag_color = (151, 151, 151)
# hare_color = (222, 222, 222)
# agent_1_color = (40, 30, 245)
# agent_2_color = (135, 135, 245)
# player_color = (45, 135, 35)
# player_2_color = (39, 194, 21)

def set_active_button(button_text):
    global active_button
    active_button = button_text



from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
)

hare_points = 1
stag_points = 3

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)
client_ID = 0
agents = [] # holds all of the sprites for the various agents.

input_rect = pygame.Rect(350, 150, 140, 32)
color_active = pygame.Color('lightskyblue3')
color_passive = pygame.Color('chartreuse4')
color = color_passive

def start_client():

    clock = pygame.time.Clock()


    username = False

    global client_ID
    #host = '192.168.30.17'  # The server's IP address
    host = '10.55.10.103'  # your local host address cause you're working from home.
    port = 12345         # The port number to connect to

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # Connect to the server
    client_socket.connect((host, port))
    # Send data to the server


    # Receive a response from the server
    while True:
        if username != False:

            game_loop(client_socket)

        else: # they need to input a username
           username = set_username(client_socket, clock, username)


                    # Close the connection
    client_socket.close()


def game_loop(client_socket):
    global client_ID, buttons_active
    server_response = None
    data = client_socket.recv(65535)

    try:  # get the stuff first
        # Deserialize the JSON response from the server
        server_response = json.loads(data.decode())

    except json.JSONDecodeError:
        pass


    if server_response != None:

        if "LEADERBOARD" in server_response:
            buttons_active = False
            draw_leaderboard(server_response["LEADERBOARD"])

        elif" INPUT" in server_response:
            add_input(server_response)

        else:
            buttons_active = True
            if "message" in server_response:
                client_ID = server_response["CLIENT_ID"]
            if "HUMAN_AGENTS" in server_response:
                initalize(server_response)
            print_board(server_response)
    message = {
        "NEW_INPUT": None,
    }
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_UP] or pressed_keys[K_DOWN] or pressed_keys[K_LEFT] or pressed_keys[K_RIGHT] or pressed_keys[K_SPACE]:
                new_input = adjust_position(pressed_keys)
                print("this is the input that we are sending ", new_input)
                if new_input == (0,0):
                    print("AAAAHAHAHAHA")
                message = {
                    "NEW_INPUT": new_input,
                    "CLIENT_ID": client_ID,
                    "INTENT" : active_button
                }

        if event.type == pygame.QUIT:
            pygame.quit()

    if buttons_active: # we need to do this here bc we need access to the events from pygame. really annoying to pass around.
        pygame_widgets.update(events)

        if active_button == "stag":
            stag_button.inactiveColour = (0, 255, 0)
            hare_button.inactiveColour = (135, 126, 126)
        if active_button == "hare":
            hare_button.inactiveColour = (0, 255, 0)
            stag_button.inactiveColour = (135, 126, 126)


    pygame.display.update()
    client_socket.send(json.dumps(message).encode())  # send a packet on every frame.


def add_input(msg):
    for agent in agents:
        agent.add_input()



def draw_leaderboard(new_leaderboard):

    SCREEN.fill(WHITECOLOR)
    # ok how the fetch do we want to do this leaderboard.
    # each slot needs: the number, the username, and the points.
    for i in range(len(new_leaderboard)):
        txt_surf = leaderboard_font.render(str(i+1) + ": " + str(new_leaderboard[i][0]) + ", " + str(new_leaderboard[i][1]), True, font_color)
        new_dest = [0,0]
        if i <= 5:
            new_dest[0] = 50
            slot = i

        else:
            new_dest[0] = 450
            slot = i-6

        new_dest[1] = slot * 140

        SCREEN.blit(txt_surf, new_dest)
#   pygame.display.update()



def initalize(server_response):
    global HUMAN_AGENTS, AI_AGENTS, HEIGHT, WIDTH, client_ID
    agents.clear()
    HUMAN_AGENTS = server_response["HUMAN_AGENTS"]
    AI_AGENTS = server_response["AI_AGENTS"]
    HEIGHT = server_response["HEIGHT"]
    WIDTH = server_response["WIDTH"]
    client_ID_list = server_response["CLIENT_ID_LIST"]

    for i in range(HUMAN_AGENTS):
        new_name = "H" + str(i+1)  # Name always needs to be H1, H2, ETC
        my_player = False
        if client_ID_list[i] == client_ID: # pretty sure there is an off by one error there.
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
    elif pressed_keys[K_DOWN]:
        curr_row += 1  # move down
    elif pressed_keys[K_LEFT]:
        curr_col -= 1  # move left
    elif pressed_keys[K_RIGHT]:
        curr_col += 1  # move right
    elif pressed_keys[K_SPACE]:
        pass
    if (curr_row, curr_col) == (0, 0) and not pressed_keys[K_SPACE]:
        print("SOMETHING BLEW UP")
    return curr_row, curr_col

def print_board(msg):
    stag_dead = False
    hare_dead = False

    HEIGHT = msg["HEIGHT"]
    WIDTH = msg["WIDTH"]
    if HEIGHT is not None or WIDTH is not None:
        draw_grid(HEIGHT, WIDTH) # draw the board first


    if "GAME_OVER" in msg:
        if "STAG_DEAD" in msg["GAME_OVER"] and msg["GAME_OVER"]["STAG_DEAD"]:
            stag_dead = msg["GAME_OVER"]["STAG_DEAD"]
        if "HARE_DEAD" in msg["GAME_OVER"] and msg["GAME_OVER"]["HARE_DEAD"]:
            hare_dead = msg["GAME_OVER"]["HARE_DEAD"]
    #print("this is the stag dead and hare_dead variables ", stag_dead, " ", hare_dead)

    if "AGENT_POSITIONS" in msg:
        highlight = False
        agents_positions = msg["AGENT_POSITIONS"]
        if "INPUT" in msg:
            highlight = True

        #calculate_points(msg["POINTS"], agents)
        for agent in agents:
            row = agents_positions[agent.name]["Y_COORD"]
            col = agents_positions[agent.name]["X_COORD"]
            new_tuple = row, col
            if agent.name == "stag":
                agent.update(SCREEN, new_tuple, dead=stag_dead)
            if agent.name == "hare":
                agent.update(SCREEN, new_tuple, dead=hare_dead)
            else:
                agent.update(SCREEN, new_tuple, highlight=highlight)
            #agent.update_points(SCREEN, new_tuple)
        draw_round(msg["CURR_ROUND"])

    if "GAME_ENDED" in msg:
        draw_game_over()

    #pygame.display.update()

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

def calculate_position(self, array_position):
    current_x = array_position[0]
    current_y = array_position[1]
    current_x = current_x * (SCREEN_WIDTH / self.width)
    current_y = current_y * (SCREEN_HEIGHT / self.height)
    return current_y, current_x


def set_next_action(self, new_row, new_col) -> None:
    self.row_to_return, self.col_to_return = new_row, new_col


def set_username(client_socket, clock, username):
    user_text = ''
    active = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False

            if event.type == pygame.KEYDOWN:
                # Check for backspace
                if event.key == pygame.K_BACKSPACE:

                    # get text input from 0 to -1 i.e. end.
                    user_text = user_text[:-1]

                    # Unicode standard is used for string
                # formation
                elif event.key == pygame.K_RETURN:
                    # send the packet!
                    message = {
                        "USERNAME": user_text,
                        "MESSAGE": "hello from the server!"
                    }
                    client_socket.send(json.dumps(message).encode())
                    username = True
                else:
                    user_text += event.unicode
                # it will set background color of screen

        if username == True:
            break
        SCREEN.fill((255, 255, 255))
        txt_surf = font.render("Please enter your username (Press Enter to submit) : ", True, font_color)
        SCREEN.blit(txt_surf, (100, 100))

        if active:
            color = color_active
        else:
            color = color_passive

            # draw rectangle and argument passed which should
        # be on screen
        pygame.draw.rect(SCREEN, color, input_rect)

        text_surface = font.render(user_text, True, (255, 255, 255))

        # render at position stated in arguments
        SCREEN.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

        # set width of textfield so that text cannot get
        # outside of user's text input
        input_rect.w = max(100, text_surface.get_width() + 10)

        # display.flip() will update only a portion of the
        # screen to updated, not full area
        pygame.display.update()

        # clock.tick(60) means that for every second at most
        # 60 frames should be passed.
        clock.tick(60)

    username = True
    return username


def change_hare(new_value):
    global preference
    preference = new_value

# yes I know it should put this in its own file, its just a pain to export as an EXE if its not all one script. Its a pain.
class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, height, width, my_player=False):
        super(Enemy, self).__init__()
        self.my_player = my_player
        self.row_to_return, self.col_to_return = None, None # for ethans code
        self.square_height = SCREEN_HEIGHT / height
        self.square_width = SCREEN_WIDTH / width
        self.name = name
        self.original_surf = pygame.surface.Surface((self.square_height, self.square_width))
        self.height, self.width = height, width
        self.square_height = self.height
        self.square_width = self.width
        self.points = 0
        self.my_player = False
        self.highlighted = False
        self.new_position = None
        self.new_surf = None
        self.screen = None

        if name == "stag":
            self.original_surf = stag_sprite
        elif name == "hare":
            self.original_surf = hare_sprite
        elif name == "R1":
            self.original_surf = other_hunter
        elif name == "R2":
            self.original_surf = other_hunter

        if name[0] == "H":
            if my_player:
                self.my_player = True
                self.original_surf = my_hunter
            else:
                self.original_surf = other_hunter

        self.surf = self.original_surf.copy()
        self.rect = self.surf.get_rect()

    def setPoints(self, newPoints):
        self.points += newPoints

    def resetPoints(self):
        self.points = 0


    def update(self, screen, array_position, highlight=False, dead=False):
        # here
        self.screen = screen
        new_position = calculate_position(self, array_position)
        self.new_position = new_position
        if dead:
            red_surf = self.surf.copy()  # Copy the original surface
            red_surf.fill((200, 60, 20))  # Fill the copy with red
            screen.blit(red_surf, new_position)  # Blit the red surface
        else:
            self.surf = self.original_surf.copy()
            screen.blit(self.surf, new_position) # so this one works.

        if highlight and self.my_player:
            print("we have become highlighted chefi. I think")
            circle_radius = self.square_width * 1.75  # for a little padding action
            position_to_plug_in = new_position[0] + (1.75 * self.square_height), new_position[1] + (1.75 * self.square_height)

            pygame.draw.circle(self.screen, (255, 0, 0), position_to_plug_in, circle_radius, 3)

    def update_alive(self):
        self.surf = self.original_surf

    def update_points(self, screen, array_position):
        if not self.name[0] == "H" and not self.name[0] == "R":  # should filter out all non agents.
            return

        new_position = calculate_position(self, array_position)
        txt_surf = font.render(str(self.points), True, font_color)
        screen.blit(txt_surf, new_position)

        # create the new font here make sure all the changes work so far tho.

    def add_input(self):
        if self.my_player:
            print("WE SHOULD BE HIGHLIGHTED HERE OR SOMETHING")
            self.highlighted = True





if __name__ == "__main__":
    start_client()