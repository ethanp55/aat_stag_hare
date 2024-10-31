import pygame
from pygame import K_ESCAPE
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

player_color = (45, 135, 35)




class Player(pygame.sprite.Sprite):
    def __init__(self, name, height, width):
        super(Player, self).__init__()

        square_height = SCREEN_HEIGHT / height
        square_width = SCREEN_WIDTH / width

        self.name = name
        self.surf = pygame.surface.Surface((square_height, square_width))
        self.height = height
        self.width = width
        self.surf.fill(player_color)
        self.rect = self.surf.get_rect()
        self.square_height = self.height
        self.square_width = self.width


    def update(self, screen, array_position, dead=False):
        new_position = calculate_position(self, array_position)
        screen.blit(self.surf, new_position)  # so this on


def calculate_position(self, array_position):
    current_x = array_position[0]
    current_y = array_position[1]
    current_x = current_x * (SCREEN_WIDTH / self.width)
    current_y = current_y * (SCREEN_HEIGHT / self.height)

    #current_x = current_x * 80 + 18  # just an offset constant
    #current_y = current_y * 80 + 18
    return current_y, current_x

