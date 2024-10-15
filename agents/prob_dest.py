from agents.agent import Agent
from environment.state import State
import numpy as np
from typing import Tuple
from utils.utils import HARE_NAME, POSSIBLE_DELTA_VALS


class ProbabilisticDestinations(Agent):
    def __init__(self, name: str, temperature: float = -1.0, max_dist: int = 3, max_iterations: int = 100) -> None:
        Agent.__init__(self, name)
        self.temperature, self.max_dist, self.max_iterations = temperature, max_dist, max_iterations

    def act(self, state: State) -> Tuple[int, int]:
        prey_row, prey_col = state.agent_positions[HARE_NAME]
        curr_row, curr_col = state.agent_positions[self.name]

        # If we are already neighbors with the prey, try to move to its current position in case it moves
        if state.neighbors(prey_row, prey_col, curr_row, curr_col):
            return prey_row, prey_col

        # Otherwise, use the softmax function to pick a distance from the prey
        curr_dist = state.n_movements(curr_row, curr_col, prey_row, prey_col)
        max_dist = max(curr_dist, self.max_dist)
        distances = range(max_dist)

        if len(distances) == 0:
            return curr_row, curr_col

        denom = sum([np.exp(dist / self.temperature) for dist in distances])
        probs = [np.exp(dist / self.temperature) / denom for dist in distances]

        for _ in range(self.max_iterations):
            desired_dist = np.random.choice(distances, p=probs)
            considerations = []

            # Find any free cells that are the selected distance from the prey
            for row in range(state.height):
                for col in range(state.width):
                    if state.is_available(row, col) and state.n_movements(row, col, prey_row, prey_col) == desired_dist:
                        dist_from_predator = state.n_movements(curr_row, curr_col, row, col)
                        considerations.append((row, col, dist_from_predator))

            if len(considerations) > 0:
                # Use the softmax function to pick one of the considered cells as the goal/destination
                considerations_denom = sum([np.exp(dist / self.temperature) for _, _, dist in considerations])
                consideration_probs = \
                    [np.exp(dist / self.temperature) / considerations_denom for _, _, dist in considerations]

                dest_idx = np.random.choice(range(len(considerations)), p=consideration_probs)
                row, col = considerations[dest_idx][0], considerations[dest_idx][1]
                d_row, d_col = state.delta_row(curr_row, row), state.delta_col(curr_col, col)
                goal, min_dist = None, np.inf

                # Find md for the largest dimension
                for delta in POSSIBLE_DELTA_VALS:
                    if d_row > d_col:
                        new_row, new_col = curr_row + delta, curr_col

                    else:
                        new_row, new_col = curr_row, curr_col + delta

                    new_row, new_col = state.adjust_vals(new_row, new_col)
                    dist = state.n_movements(curr_row, curr_col, new_row, new_col)

                    if dist < min_dist and state.is_available(new_row, new_col):
                        goal = new_row, new_col
                        min_dist = dist

                if goal is not None:
                    return goal

        # If we have tried multiple iterations and cannot find a place to move, just stay where we are
        return curr_row, curr_col
