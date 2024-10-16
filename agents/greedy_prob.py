from agents.agent import Agent
from environment.state import State
import numpy as np
from typing import Tuple
from utils.utils import HARE_NAME, POSSIBLE_DELTA_VALS


class GreedyProbabilistic(Agent):
    def __init__(self, name: str, dimension_temp: float = 0.5, direction_temp: float = -0.5,
                 occupied_penalty: float = 2.0) -> None:
        Agent.__init__(self, name)
        self.dimension_temp, self.direction_temp, self.occupied_penalty = \
            dimension_temp, direction_temp, occupied_penalty

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        prey_row, prey_col = state.agent_positions[HARE_NAME]
        curr_row, curr_col = state.agent_positions[self.name]
        prey_neighboring_positions = state.neighboring_positions(prey_row, prey_col)

        # If we are already neighbors with the prey, try to move to its current position in case it moves
        if state.neighbors(prey_row, prey_col, curr_row, curr_col):
            return prey_row, prey_col

        # Otherwise, find the closest cell neighboring the prey and set that as the goal/destination
        goal, d_row, d_col, min_dist = None, None, None, np.inf

        for row, col in prey_neighboring_positions:
            dist = state.n_movements(curr_row, curr_col, row, col)

            if dist < min_dist:
                goal = row, col
                d_row, d_col = state.delta_row(curr_row, row), state.delta_col(curr_col, col)
                min_dist = dist

        # If we can't move, stay at the current position
        if goal is None:
            return curr_row, curr_col

        # Use the softmax function to decide if we should travel in the row or column dimension
        p_row = np.exp(d_row / self.dimension_temp) / \
            (np.exp(d_row / self.dimension_temp) + np.exp(d_col / self.dimension_temp))

        use_row = np.random.choice([True, False], p=[p_row, 1 - p_row])

        # Calculate md and md hat as defined in the paper
        md, md_delta, min_dist = None, None, np.inf

        for delta in POSSIBLE_DELTA_VALS:
            if use_row:
                new_row, new_col = curr_row + delta, curr_col

            else:
                new_row, new_col = curr_row, curr_col + delta

            new_row, new_col = state.adjust_vals(new_row, new_col)
            dist = state.n_movements(new_row, new_col, curr_row, curr_col)

            if not state.is_available(new_row, new_col):
                dist += self.occupied_penalty

            if dist < min_dist:
                md = new_row, new_col
                md_delta, min_dist = delta, dist

        md_hat = (md[0] - md_delta, md[1]) if use_row else (md[0], md[1] - md_delta)  # md hat is a move in the opposite direction
        md_hat = state.adjust_vals(md_hat[0], md_hat[1])
        md_hat_dist = state.n_movements(curr_row, curr_col, md_hat[0], md_hat[1])

        if not state.is_available(md_hat[0], md_hat[1]):
            md_hat_dist += self.occupied_penalty

        # Use the softmax function to decide if we should use md or md hat
        p_md = np.exp(min_dist / self.direction_temp) / \
            (np.exp(min_dist / self.direction_temp) + np.exp(md_hat_dist / self.direction_temp))

        use_md = np.random.choice([True, False], p=[p_md, 1 - p_md])

        return md if use_md else md_hat
