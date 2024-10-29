from operator import truediv

import pygame
from pygame import K_ESCAPE
from pygame.examples.moveit import WIDTH, HEIGHT
from gui import player
from gui import enemy
from environment.runner import run
from agents.random_agent import *
from agents.human import *
from environment.world import StagHare

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

hunters = [Random(name="R1"),Random(name="R2"),Random(name="H")] # creates our agents for our environment

SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.

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
    while running:

        draw_grid()

        states = stag_hare.return_state()



        for event in pygame.event.get():

            for agent in states.agent_positions:
                if agent == 'hare':
                    pass
                if agent == "stag":
                    pass
                if agent == "R1":
                    pass
                if agent == "R2":
                    pass
                if agent == "H":
                    pass

            pressed_keys = pygame.key.get_pressed()



            SCREEN.blit(this_player.surf, this_player.rect)
            current_tuple = 9,9
            stag.update(SCREEN, current_tuple)



            this_player.update(pressed_keys)
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

if __name__ == '__main__':
    main()


def calculate_position(row, column):
    new_x_coord = (row * width) + 10 # centering constant IG.
    new_y_coord = (column * height) + 10
    return new_x_coord, new_y_coord

