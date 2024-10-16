from environment.state import State
import numpy as np
from typing import Tuple
from utils.utils import POSSIBLE_DELTA_VALS, POSSIBLE_MOVEMENTS, VERTICAL


class Agent:
    def __init__(self, name: str) -> None:
        self.name = name

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        pass

    def random_action(self, state: State) -> Tuple[int, int]:
        curr_row, curr_col = state.agent_positions[self.name]
        movement = np.random.choice(POSSIBLE_MOVEMENTS)
        delta = np.random.choice(POSSIBLE_DELTA_VALS)

        if movement == VERTICAL:
            return curr_row + delta, curr_col

        else:
            return curr_row, curr_col + delta
