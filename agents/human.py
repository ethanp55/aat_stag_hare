from agents.agent import Agent
from environment.state import State
from typing import Tuple



from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)


class humanAgent:
    def __init__(self, name) -> None:
        Agent.__init__(self, name)
        self.name = name
        self.row_to_return, self.col_to_return = None, None

    def set_next_action(self, new_row, new_col) -> None:
        self.row_to_return, self.col_to_return = new_row, new_col

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        return self.row_to_return, self.col_to_return

