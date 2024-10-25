from operator import truediv

import pygame
from pygame import K_ESCAPE
from environment.runner import run

# i know for a fact that I need at least these 2.
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

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((75, 25))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT



pygame.init() # actually starts the game.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # not sure what the preferred game size is but lets start there IG.

player = Player()

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