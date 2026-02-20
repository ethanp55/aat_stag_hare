# version of my old gui that we ran through chat and got to work. trying to figure out what teh differences are as we speek.

from operator import truediv
import pygame
import sys
import time
from pygame import K_ESCAPE
from gui import player
from gui import enemy
from agents.random_agent import *
from agents.human import *
from environment.world import StagHare
from agents.alegaatr import AlegAATr
from agents.dqn import DQNAgent
from agents.qalegaatr import QAlegAATr
from agents.aleqgaatr import AleqgAATr
from agents.smalegaatr import SMAlegAATr
from agents.rawo import RawO

PAUSE_TIME = 3
HEIGHT = 10
WIDTH = 10

BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

hunters = [AlegAATr(name='R1', lmbda=0.0, ml_model_type='knn', enhanced=True),
           AlegAATr(name='R2', lmbda=0.0, ml_model_type='knn', enhanced=True),
           humanAgent(name='H')]

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
preference = False

# Initialize pygame and create screen
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Stag Hunt Game")


def draw_grid(height, width):
    """Draw the grid on the screen."""
    SCREEN.fill(WHITECOLOR)
    widthOffset = SCREEN_WIDTH / width
    heightOffset = SCREEN_HEIGHT / height
    for x in range(width):
        for y in range(height):
            rect = pygame.Rect(x * widthOffset, y * heightOffset,
                               widthOffset, heightOffset)
            pygame.draw.rect(SCREEN, BLACKCOLOR, rect, 1)


# no boundary checking. moving offscreen is intentional.
def set_player_position(pressed_keys, state):

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


def main():
    # Initialize game objects
    this_player = player.Player("player", HEIGHT, WIDTH)
    stag = enemy.Enemy("stag", HEIGHT, WIDTH)
    hare = enemy.Enemy("hare", HEIGHT, WIDTH)
    agent1 = enemy.Enemy("agent1", HEIGHT, WIDTH)
    agent2 = enemy.Enemy("agent2", HEIGHT, WIDTH)

    # Initialize game state
    while True:
        stag_hare = StagHare(HEIGHT, WIDTH, hunters)
        if not stag_hare.is_over():
            break

    running = True
    rewards = [0] * (len(hunters) + 2)
    clock = pygame.time.Clock()  # Add a clock to control frame rate

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        # Draw grid
        draw_grid(HEIGHT, WIDTH)

        # Get current state
        state = stag_hare.return_state()

        # Handle player input
        pressed_keys = pygame.key.get_pressed()
        if any([pressed_keys[K_UP], pressed_keys[K_DOWN],
                pressed_keys[K_LEFT], pressed_keys[K_RIGHT]]):
            new_row, new_col = set_player_position(pressed_keys, state)
            hunters[-1].set_next_action(new_row, new_col)

            # Make the game transition
            round_rewards = stag_hare.transition()

            # Update rewards
            for i, reward in enumerate(round_rewards):
                rewards[i] += reward

        # Draw all agents
        for agent in state.agent_positions:
            pos = state.agent_positions[agent]
            if agent == 'hare':
                hare.update(SCREEN, pos)
            elif agent == "stag":
                stag.update(SCREEN, pos)
            elif agent == "R1":
                agent1.update(SCREEN, pos)
            elif agent == "R2":
                agent2.update(SCREEN, pos)
            elif agent == "H":
                this_player.update(SCREEN, pos)

        # Check if game is over
        if stag_hare.is_over():
            if stag_hare.state.hare_captured():
                hare.update(SCREEN, state.agent_positions["hare"], True)
            else:
                stag.update(SCREEN, state.agent_positions["stag"], True)
            pygame.display.update()
            time.sleep(PAUSE_TIME)
            running = False

        # Update display
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()


if __name__ == '__main__':
    main()