from operator import truediv

import pygame
from pygame import K_ESCAPE
import player


from environment.runner import run
from agents.random_agent import *
from agents.human import *

# number of rows and columns.
height = 10
width = 10



hunters = [Random(name="R1"),Random(name="R2"),Random(name="H")]
run(hunters, height=height, width=width) # how the mcfetch do I access the stag and the hare, I can't find them anywhere. probably need to set them up as values IG.




SCREEN_WIDTH = 800 # fetch it we are making it a square.
SCREEN_HEIGHT = 800

human_player = pygame.Surface((20,20)) # creates a little player object
human_player.fill((0,120,120))
human_rect_text = human_player.get_rect()


pygame.init() # actually starts the game.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # not sure what the preferred game size is but lets start there IG.

player = player.Player()

running = True
while running:
    for event in pygame.event.get():
        pressed_keys = pygame.key.get_pressed()

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE: #gives us a way to stop execution.
                running = False
            # now we need to pass off the movement.
            #

        # need to handle 4 events
        #1. process user input
        #2. udpates the state of the game objects
        #3. updates the display (and audio output)
        #4. maintains the speed of the game.

        # so the way I understand it
        # we need to import the size of the game from the actual environment and update them as we go
        # blit the lines on the screen and make them black
        # fill the backround with white (which we already did)
        # what I don't understand is how to update the environment to contain those agents as specified.
        # I don't know how to make the user input actually interact with anything, which is prolly the bigggest problem
        # I also don't know if the output is dynamic or static - if moves are made once every couple of seconds or the second
        # that new player input is available it executes everything. more questions for me to ask IG lol.
        # I wish I could just run this and understand how it works, that would make this a lot easier.

        screen.fill((0,0,0))
        screen.blit(player.surf, player.rect)
        player.update(pressed_keys)
        pygame.display.flip()

pygame.quit()