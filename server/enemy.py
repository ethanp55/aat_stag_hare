from array import array

import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

stag_color = (151, 151, 151)
hare_color = (222, 222, 222)
agent_1_color = (40, 30, 245)
agent_2_color = (135, 135, 245)
player_color = (45, 135, 35)
player_2_color = (130, 130, 130)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, height, width):
        super(Enemy, self).__init__()
        self.row_to_return, self.col_to_return = None, None # for ethans code
        square_height = SCREEN_HEIGHT / height
        square_width = SCREEN_WIDTH / width
        self.name = name
        self.surf = pygame.surface.Surface((square_height, square_width))
        self.height, self.width = height, width
        self.square_height = self.height
        self.square_width = self.width

        if name == "stag":
            self.surf.fill(stag_color)
        elif name == "hare":
            self.surf.fill(hare_color)
        elif name == "R1":
            self.surf.fill(agent_1_color)
        elif name == "R2":
            self.surf.fill(agent_2_color)
        elif name == "H1":
            self.surf.fill(player_color)
        elif name == "H2":
            self.surf.fill(player_2_color)

        self.rect = self.surf.get_rect()


    def update(self, screen, array_position, dead=False):
        # here
        new_position = calculate_position(self, array_position)
        if dead:
            self.surf.fill((200, 60, 20))
            screen.blit(self.surf, new_position)
        else:
            screen.blit(self.surf, new_position) # so this one works.


def calculate_position(self, array_position):
    current_x = array_position[0]
    current_y = array_position[1]
    current_x = current_x * (SCREEN_WIDTH / self.width)
    current_y = current_y * (SCREEN_HEIGHT / self.height)
    return current_y, current_x


def set_next_action(self, new_row, new_col) -> None:
    self.row_to_return, self.col_to_return = new_row, new_col