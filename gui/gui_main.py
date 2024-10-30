from operator import truediv

import pygame
from pygame import K_ESCAPE
from gui import player
from gui import enemy
from agents.random_agent import *
from agents.human import *
from environment.world import StagHare
from agents.alegaatr import AlegAATr
from agents.dqn import DQNAgent

#the state contains the position methinks.

# pre load in all of our sprites as well.
HUNTER_SPRITE = pygame.image.load("hunter.png") # for the human player thingy.
HARE_IMAGE = pygame.image.load("hare.png") # might need to make this smaller ig.
STAG_IMAGE = pygame.image.load("stag.png") # might also need to make this smaller.
AGENT_IMAGE = pygame.image.load("agent.png") # hehe funny joke.

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

# number of rows and columns.
height = 10
width = 10

hunters = [Random(name='R1'), Random(name='R2'), humanAgent(name='H')]
# hunters = [AlegAATr(name='R1', lmbda=0.0, ml_model_type='knn', enhanced=True),
#            AlegAATr(name='R2', lmbda=0.0, ml_model_type='knn', enhanced=True),
#            humanAgent(name='H')]
# hunters = [DQNAgent(name='R1'),
#            DQNAgent(name='R2'),
#            humanAgent(name='H')]

SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.


from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)


# sets up and initializes all of our agents
this_player = player.Player()
stag = enemy.Enemy(STAG_IMAGE)
hare = enemy.Enemy(HARE_IMAGE)
agent1 = enemy.Enemy(AGENT_IMAGE)
agent2 = enemy.Enemy(AGENT_IMAGE)
play_test_player = player.Player()


def main():
    pygame.init()  # actually starts the game.
    running = True
    rewards = [0] * (len(hunters) + 2)

    while True:
        stag_hare = StagHare(height, width, hunters)
        if not stag_hare.is_over():
            break

    while running and not stag_hare.is_over(): # make sure that we aren't over

        draw_grid()

        state = stag_hare.return_state()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                pressed_keys = pygame.key.get_pressed()

                new_row, new_col = set_player_position(pressed_keys, state)
                hunters[-1].set_next_action(new_row, new_col)

                round_rewards = stag_hare.transition()

                # Update rewards
                for i, reward in enumerate(round_rewards):
                    rewards[i] += reward


            for agent in state.agent_positions:
                if agent == 'hare':
                    hare.update(SCREEN, state.agent_positions[agent])
                if agent == "stag":
                    stag.update(SCREEN, state.agent_positions[agent])
                if agent == "R1":
                    agent1.update(SCREEN, state.agent_positions[agent])
                if agent == "R2":
                    agent2.update(SCREEN, state.agent_positions[agent])
                if agent == "H":
                    #current_position = (3,2)
                    #this_player.update(SCREEN, current_position)
                    this_player.update(SCREEN, state.agent_positions[agent])


            pygame.display.update()

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:  # gives us a way to stop execution.
                    running = False

    pygame.quit()


def draw_grid(): # draws the grid on every frame just so we have it.
    SCREEN.fill(WHITECOLOR)
    widthOffset = (SCREEN_WIDTH / width)
    heightOffset = (SCREEN_HEIGHT / height)
    for x in range(0, width):
        for y in range(0, height):
            rect = pygame.Rect(x*widthOffset, y*heightOffset, widthOffset, heightOffset)
            pygame.draw.rect(SCREEN, BLACKCOLOR, rect, 1)



def set_player_position(pressed_keys, state):

    # so left and up are mixed, as are down and right. I couldn't tell you why. \
    # also you can currently escape by either going left or up but I think that might be intended. 

    curr_row, curr_col = state.agent_positions["H"] # because thats the name of the human player
    if pressed_keys[K_UP]:
        curr_row -= 1
    if pressed_keys[K_DOWN]:
        curr_row += 1  # move down
    if pressed_keys[K_LEFT]:
        curr_col -= 1  # move left
    if pressed_keys[K_RIGHT]:
        curr_col += 1  # move right

    return curr_row, curr_col

if __name__ == '__main__':
    main()



