from operator import truediv

import pygame
from pygame import K_ESCAPE
from gui import player
from gui import enemy
from agents.random_agent import *
from agents.human import *
from environment.world import StagHare

#the state contains the position methinks.

# pre load in all of our sprites as well.
HUNTER_SPRITE = pygame.image.load("hunter.png") # for the human player thingy.
HARE_IMAGE = pygame.image.load("hare.png") # might need to make this smaller ig.
STAG_IMAGE = pygame.image.load("stag.png") # might also need to make this smaller.
AGENT_IMAGE = pygame.image.load("agent.png") # hehe funny joke.

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

# number of rows and columns.
height = 10
width = 10

hunters = [Random(name="R1"),Random(name="R2"),humanAgent(name="H")] # creates our agents for our environment

SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.


from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)


# sets up and initializes all of our agents
this_player = player.Player()
stag = enemy.Enemy(STAG_IMAGE)
hare = enemy.Enemy(HARE_IMAGE)
agent1 = enemy.Enemy(AGENT_IMAGE)
agent2 = enemy.Enemy(AGENT_IMAGE)

def main():
    pygame.init()  # actually starts the game.
    running = True

    stag_hare = StagHare(height, width, hunters)
    while running and not stag_hare.is_over(): # make sure that we aren't over

        draw_grid()
        rewards = [0] * (len(hunters) + 2)

        state = stag_hare.return_state()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                pressed_keys = pygame.key.get_pressed()

                state.agent_positions["H"] = set_player_position(pressed_keys, state)
                round_rewards = stag_hare.gui_transition() # magic

                # Update rewards
                for i, reward in enumerate(round_rewards):
                    rewards[i] += reward

                stag_hare.gui_transition()  # this is where a lot of the magic happens.


            for agent in state.agent_positions:
                if agent == 'hare':
                    hare.update(SCREEN, state.agent_positions[agent])
                if agent == "stag":
                    stag.update(SCREEN, state.agent_positions[agent])
                if agent == "R1":
                    agent1.update(SCREEN, state.agent_positions[agent])
                if agent == "R2":
                    agent2.update(SCREEN, state.agent_positions[agent])
                if agent == "H":
                    this_player.update(SCREEN, state.agent_positions[agent])


            pygame.display.update()

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:  # gives us a way to stop execution.
                    running = False

    pygame.quit()


def draw_grid(): # draws the grid on every frame just so we have it.
    SCREEN.fill(WHITECOLOR)
    widthOffset = (SCREEN_WIDTH / width)
    heightOffset = (SCREEN_HEIGHT / height)
    for x in range(0, width):
        for y in range(0, height):
            rect = pygame.Rect(x*widthOffset, y*heightOffset, widthOffset, heightOffset)
            pygame.draw.rect(SCREEN, BLACKCOLOR, rect, 1)


def calculate_position(row, column):
    new_x_coord = (row * width) + 10 # centering constant IG.
    new_y_coord = (column * height) + 10
    return new_y_coord, new_x_coord

def set_player_position(pressed_keys, state):
    curr_row, curr_col = state.agent_positions["H"] # because thats the name of the human player
    if pressed_keys[K_UP]:
        curr_row += 1 # move left
    if pressed_keys[K_DOWN]:
        curr_row -= 1 # move right
    if pressed_keys[K_LEFT]:
        curr_col -= 1 # move up
    if pressed_keys[K_RIGHT]:
        curr_col += 1 # move down
    return curr_row, curr_col

if __name__ == '__main__':
    main()



