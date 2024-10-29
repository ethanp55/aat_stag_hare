from agents.agent import Agent
from environment.state import State
from typing import Tuple

row = 0
col = 0

from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)


class humanAgent:
    def __init__(self, name) -> None:
        Agent.__init__(self, name)


    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        pass

    def get_player_position(self):
        curr_row, curr_col = state.agent_positions[self.name]

    def set_player_position(self, row, col):
        self.row = row
        self.col = col
