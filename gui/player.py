import pygame
from pygame import K_ESCAPE
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

HUNTER_SPRITE = pygame.image.load("hunter.png") # for the human player thingy.



from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)



class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.image = HUNTER_SPRITE
        self.surf = HUNTER_SPRITE
        self.rect = self.image.get_rect()


    def update(self, screen, array_position):
        new_position = calculate_position(array_position)
        screen.blit(self.surf, new_position)  # so this one works.


def calculate_position(array_position):
    current_x = array_position[0]
    current_y = array_position[1]
    # current_y = 10 - current_y # need to flip

    current_x = current_x * 80 + 18  # just an offset constant
    current_y = current_y * 80 + 18
    return current_x, current_y

