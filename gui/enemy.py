from array import array

import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800


class Enemy(pygame.sprite.Sprite):
    def __init__(self, sprite):
        super(Enemy, self).__init__()
        self.image = sprite
        self.surf = sprite
        self.rect = self.image.get_rect()

    def update(self, screen, array_position):
        # here
        new_position = calculate_position(array_position)

        screen.blit(self.surf, new_position) # so this one works.




def calculate_position(array_position):
    current_x = array_position[0]
    current_y = array_position[1]
    current_x = current_x * 80 + 18 # just an offset constant
    current_y = current_y * 80 + 18
    return current_x, current_y
