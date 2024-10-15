from agents.agent import Agent
from environment.state import State
from typing import Tuple
from utils.a_star import AStar
from utils.utils import HARE_NAME, STAG_NAME


class TeamAware(Agent):
    def __init__(self, name: str) -> None:
        Agent.__init__(self, name)

    def act(self, state: State) -> Tuple[int, int]:
        stag_row, stag_col = state.agent_positions[STAG_NAME]
        curr_row, curr_col = state.agent_positions[self.name]
        stag_neighboring_positions = state.neighboring_positions(stag_row, stag_col)

        # If we are already neighbors with the stag, try to move to its current position in case it moves
        if state.neighbors(stag_row, stag_col, curr_row, curr_col):
            return stag_row, stag_col

        # Calculate the distance from each hunter to each available cell neighboring the stag
        neighbor_distances, name_ordering = {}, []

        for agent_name, curr_pos in state.agent_positions.items():
            # Ignore the prey
            if agent_name == STAG_NAME or agent_name == HARE_NAME:
                continue

            row, col = curr_pos

            # The hunter is already a neighbor of the stag
            if state.neighbors(stag_row, stag_col, row, col):
                continue

            distances = []

            for new_row, new_col in stag_neighboring_positions:
                dist = state.n_movements(row, col, new_row, new_col)
                distances.append((new_row, new_col, dist))

            # Sort by distance
            distances.sort(key=lambda x: x[-1])
            neighbor_distances[agent_name] = distances

            # Keep track of the worst shortest distance
            name_ordering.append((agent_name, distances[-1][-1]))

        # Order by the worst shortest distance
        name_ordering.sort(key=lambda x: x[-1])
        assigned, goal = set(), None

        # Make assignments - assign the goal when we reach ourselves so that we can plan a path
        for agent_name, _ in name_ordering:
            for row, col, _ in neighbor_distances[agent_name]:
                if (row, col) not in assigned:
                    assigned.add((row, col))

                    if agent_name == self.name:
                        goal = (row, col)

                    break

        # If we can't move, stay at the current position
        if goal is None:
            return curr_row, curr_col

        goal_row, goal_col = goal

        return AStar.find_path(curr_row, curr_col, goal_row, goal_col, state)
