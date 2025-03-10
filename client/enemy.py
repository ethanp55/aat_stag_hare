from array import array

import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

stag_color = (151, 151, 151)
hare_color = (222, 222, 222)
agent_1_color = (40, 30, 245)
agent_2_color = (135, 135, 245)
player_color = (45, 135, 35)
player_2_color = (39, 194, 21)



pygame.font.init()
font = pygame.font.Font(None, 32) # might need to dynamically allocate the font.
font_color = (100, 200, 150)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, height, width, my_player=False):
        super(Enemy, self).__init__()
        self.row_to_return, self.col_to_return = None, None # for ethans code
        square_height = SCREEN_HEIGHT / height
        square_width = SCREEN_WIDTH / width
        self.name = name
        self.surf = pygame.surface.Surface((square_height, square_width))
        self.height, self.width = height, width
        self.square_height = self.height
        self.square_width = self.width
        self.points = 0

        if name == "stag":
            self.surf.fill(stag_color)
        elif name == "hare":
            self.surf.fill(hare_color)
        elif name == "R1":
            self.surf.fill(agent_1_color)
        elif name == "R2":
            self.surf.fill(agent_2_color)

        if name[0] == "H":
            if my_player:
                self.surf.fill(player_color)
            else:
                self.surf.fill(player_2_color)


        self.rect = self.surf.get_rect()

    def setPoints(self, newPoints):
        self.points += newPoints

    def resetPoints(self):
        self.points = 0


    def update(self, screen, array_position, dead=False):
        # here
        new_position = calculate_position(self, array_position)
        if dead:
            self.surf.fill((200, 60, 20))
            screen.blit(self.surf, new_position)
        else:
            self.update_alive()
            screen.blit(self.surf, new_position) # so this one works.

    def update_alive(self):
        if self.name == "stag":
            self.surf.fill(stag_color)
        elif self.name == "hare":
            self.surf.fill(hare_color)



    def update_points(self, screen, array_position):
        if not self.name[0] == "H" and not self.name[0] == "R":  # should filter out all non agents.
            return

        new_position = calculate_position(self, array_position)
        txt_surf = font.render(str(self.points), True, font_color)
        screen.blit(txt_surf, new_position)

        # create the new font here make sure all the changes work so far tho.


def calculate_position(self, array_position):
    current_x = array_position[0]
    current_y = array_position[1]
    current_x = current_x * (SCREEN_WIDTH / self.width)
    current_y = current_y * (SCREEN_HEIGHT / self.height)
    return current_y, current_x


def set_next_action(self, new_row, new_col) -> None:
    self.row_to_return, self.col_to_return = new_row, new_col