import pygame
from pygame import K_ESCAPE
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800




class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((400, 400))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()

    def update(self, pressed_keys):
        pass
        # update, instead of pressed keys, will take in the new position and upate it to the appropriate cell and center it.
        # something something new state something something


