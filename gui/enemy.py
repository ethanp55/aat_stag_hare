from array import array

import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

stag_color = (151, 151, 151)
hare_color = (222, 222, 222)
agent_1_color = (40, 30, 245)
agent_2_color = (135, 135, 245)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, height, width):
        super(Enemy, self).__init__()

        square_height = SCREEN_HEIGHT / height
        square_width = SCREEN_WIDTH / width

        self.name = name
        self.surf = pygame.surface.Surface((square_height, square_width))
        self.height, self.width = height, width

        if name == "stag":
            self.surf.fill(stag_color)
        elif name == "hare":
            self.surf.fill(hare_color)
        elif name == "agent1":
            self.surf.fill(agent_1_color)
        elif name == "agent2":
            self.surf.fill(agent_2_color)

        self.rect = self.surf.get_rect()

    def update(self, screen, array_position):
        # here
        new_position = calculate_position(self, array_position)

        screen.blit(self.surf, new_position) # so this one works.




def calculate_position(self, array_position):
    current_x = array_position[0]
    current_y = array_position[1]
    current_x = current_x * (SCREEN_WIDTH / self.width)
    current_y = current_y * (SCREEN_HEIGHT / self.height)
    return current_y, current_x
