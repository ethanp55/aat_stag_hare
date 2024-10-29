from operator import truediv

import pygame
from pygame import K_ESCAPE
from pygame.examples.moveit import WIDTH, HEIGHT
from gui import player
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


def main():
    human_player = pygame.Surface((20, 20))  # creates a little player object
    human_player.fill((0, 120, 120))
    human_rect_text = human_player.get_rect()

    pygame.init()  # actually starts the game.
    this_player = player.Player()



    running = True

    #stag_hare = StagHare(height, width, hunters)




    while running:

        draw_grid()

        #states = stag_hare.return_state()

        for event in pygame.event.get():

            pressed_keys = pygame.key.get_pressed()

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:  # gives us a way to stop execution.
                    running = False
                # now we need to pass off the movement.
                #

            # i need a rect for all of the players,
            # then a separate one for the stag and the hare
            # and maybe have a different class for the player vs the non players.

            # need to handle 4 events
            # 1. process user input
            # 2. udpates the state of the game objects
            # 3. updates the display (and audio output)
            # 4. maintains the speed of the game.

            # so the way I understand it
            # we need to import the size of the game from the actual environment and update them as we go
            # blit the lines on the screen and make them black
            # fill the backround with white (which we already did)
            # what I don't understand is how to update the environment to contain those agents as specified.
            # I don't know how to make the user input actually interact with anything, which is prolly the bigggest problem
            # I also don't know if the output is dynamic or static - if moves are made once every couple of seconds or the second
            # that new player input is available it executes everything. more questions for me to ask IG lol.
            # I wish I could just run this and understand how it works, that would make this a lot easier.

            SCREEN.blit(this_player.surf, this_player.rect)
            this_player.update(pressed_keys)
            pygame.display.update()

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
