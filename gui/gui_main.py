from operator import truediv

import pygame
from pygame import K_ESCAPE
import player
from environment.runner import run

# i know for a fact that I need at least these 2.
# i know for a fact that I need at least these 2.
import environment
import agents


# need to make a couple of agents IG lol


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

        screen.fill((0,0,0))
        screen.blit(player.surf, player.rect)
        player.update(pressed_keys)
        pygame.display.flip()

pygame.quit()