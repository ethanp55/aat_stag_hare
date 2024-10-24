from operator import truediv

import pygame
from pygame import K_ESCAPE

# i know for a fact that I need at least these 2.
import environment
import agents

#from pygame.locals import *  # I could do that I guess, I think I'm gonna want to limit actions tho
from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)

SCREEN_WIDTH = 800 # fetch it we are making it a square.
SCREEN_HEIGHT = 800

human_player = pygame.Surface((20,20)) # creates a little player object
human_player.fill((0,120,120))
human_rect_text = human_player.get_rect()



pygame.init() # actually starts the game.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # not sure what the preferred game size is but lets start there IG.


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE: #gives us a way to stop execution.
                running = False
            # now we need to pass off the movement.

        # need to handle 4 events
        #1. process user input
        #2. udpates the state of the game objects
        #3. updates the display (and audio output)
        #4. maintains the speed of the game.

    screen.fill((255,255,255))

    pygame.draw.circle(screen, (0,0,255), (400, 400), 75)

    pygame.display.update()

pygame.quit()