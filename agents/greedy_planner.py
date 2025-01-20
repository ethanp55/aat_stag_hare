from agents.agent import Agent
from environment.state import State
import numpy as np
from typing import Tuple
from utils.a_star import AStar
from utils.utils import HARE_NAME, STAG_NAME


class GreedyPlanner(Agent):
    def __init__(self, name: str, target: str) -> None:
        Agent.__init__(self, name)
        assert target == HARE_NAME or target == STAG_NAME
        self.target = target

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        prey_row, prey_col = state.agent_positions[self.target]
        curr_row, curr_col = state.agent_positions[self.name]

        # If we are already neighbors with the prey, try to move to its current position in case it moves
        if state.neighbors(prey_row, prey_col, curr_row, curr_col):
            return prey_row, prey_col

        prey_neighboring_positions, min_dist, goal = state.neighboring_positions(prey_row, prey_col), np.inf, None

        for row, col in prey_neighboring_positions:
            dist = state.n_movements(curr_row, curr_col, row, col)

            if dist < min_dist:
                goal, min_dist = (row, col), dist

        # If we can't move, stay at the current position
        if goal is None:
            return curr_row, curr_col

        goal_row, goal_col = goal

        return AStar.find_path(curr_row, curr_col, goal_row, goal_col, state)

    def is_hunting_hare(self) -> bool:
        return self.target == HARE_NAME
