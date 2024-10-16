import numpy as np
from typing import Dict, List, Tuple
from utils.utils import AVAILABLE, HARE_NAME, HARE_REWARD, MAX_MOVEMENT_UNITS, N_HUNTERS, N_REQUIRED_TO_CAPTURE_HARE, \
    N_REQUIRED_TO_CAPTURE_STAG, POSSIBLE_DELTA_VALS, POSSIBLE_MOVEMENTS, STAG_NAME, STAG_REWARD, VERTICAL


class State:
    def __init__(self, height: int, width: int, agent_names: List[str]) -> None:
        self.height, self.width, self.agent_positions, self.round_num = height, width, {}, 0
        self.agent_names = agent_names

        # Initialize the grid
        self.grid = []

        for _ in range(self.height):
            new_row = [AVAILABLE for _ in range(self.width)]
            self.grid.append(new_row)

        assert len(self.grid) == self.height and len(self.grid[0]) == self.width

        # Randomly assign starting positions for the hunters, hare, and stag
        for i, agent_name in enumerate(agent_names):
            while True:
                row_index = np.random.choice(list(range(self.height)))
                col_index = np.random.choice(list(range(self.width)))

                if self.grid[row_index][col_index] == AVAILABLE:
                    self.grid[row_index][col_index] = i
                    self.agent_positions[agent_name] = (row_index, col_index)
                    break

    def __hash__(self):
        return hash(str(self.grid))

    def __str__(self):
        grid_str = ''

        for row in self.grid:
            grid_str += f'{row}\n'

        return grid_str[:-1]

    # Same as prev two, but for the other hunters
    def vector_representation(self, hunter_name: str) -> np.array:
        # Grid dimensions
        n_rows, n_cols = self.height, self.width

        # The hunter's position
        curr_row, curr_col = self.agent_positions[hunter_name]
        my_x, my_y = curr_row / self.height, curr_col / self.width

        # The positions of the hare and stag
        hare_row, hare_col = self.agent_positions[HARE_NAME]
        stag_row, stag_col = self.agent_positions[STAG_NAME]
        hare_x, hare_y = hare_row / self.height, hare_col / self.width
        stag_x, stag_y = stag_row / self.height, stag_col / self.width

        # The hunter's distance to the hare and stag
        n_possible_steps = self.height * self.width
        dist_to_hare = self.n_movements(curr_row, curr_col, hare_row, hare_col)
        dist_to_stag = self.n_movements(curr_row, curr_col, stag_row, stag_col)
        my_dist_to_hare, my_dist_to_stag = dist_to_hare / n_possible_steps, dist_to_stag / n_possible_steps

        # The other hunters' distance to the hare and stag
        other_hunters_dists_to_hare, other_hunters_dist_to_stag = [], []
        for agent_name, (row, col) in self.agent_positions.items():
            if agent_name == HARE_NAME or agent_name == STAG_NAME or agent_name == hunter_name:
                continue

            dist_to_hare = self.n_movements(row, col, hare_row, hare_col)
            dist_to_stag = self.n_movements(row, col, stag_row, stag_col)
            their_dist_to_hare, their_dist_to_stag = dist_to_hare / n_possible_steps, dist_to_stag / n_possible_steps
            other_hunters_dists_to_hare.append(their_dist_to_hare)
            other_hunters_dist_to_stag.append(their_dist_to_stag)
        assert len(other_hunters_dists_to_hare) == len(other_hunters_dist_to_stag) == N_HUNTERS - 1

        # Combine everything
        list_representation = [n_rows, n_cols, my_x, my_y, hare_x, hare_y, stag_x, stag_y, my_dist_to_hare,
                               my_dist_to_stag] + other_hunters_dists_to_hare + other_hunters_dist_to_stag

        # Convert to numpy array, return
        return np.array(list_representation)

    def available_actions(self) -> Dict[str, List[Tuple[int, int]]]:
        possible_actions_map = {}

        for agent_name, curr_pos in self.agent_positions.items():
            curr_row, curr_col = curr_pos

            for movement in POSSIBLE_MOVEMENTS:
                for delta in POSSIBLE_DELTA_VALS:
                    if movement == VERTICAL:
                        new_row, new_col = curr_row + delta, curr_col

                    else:
                        new_row, new_col = curr_row, curr_col + delta

                    new_row, new_col = self.adjust_vals(new_row, new_col)
                    possible_positions = possible_actions_map.get(agent_name, [])

                    if (new_row, new_col) not in possible_positions:
                        possible_positions.append((new_row, new_col))

                    possible_actions_map[agent_name] = possible_positions

        return possible_actions_map

    def adjust_vals(self, row_val: int, col_val: int) -> Tuple[int, int]:
        row, col = row_val, col_val

        if row_val < 0:
            row = self.height - 1

        elif row_val >= self.height:
            row = 0

        if col_val < 0:
            col = self.width - 1

        elif col_val >= self.width:
            col = 0

        return row, col

    def is_available(self, row_val: int, col_val: int) -> bool:
        row, col = self.adjust_vals(row_val, col_val)

        return self.grid[row][col] == AVAILABLE

    def hunter_in_position(self, row_val: int, col_val: int) -> bool:
        row, col = self.adjust_vals(row_val, col_val)
        hare_row, hare_col = self.agent_positions[HARE_NAME]
        stag_row, stag_col = self.agent_positions[STAG_NAME]

        not_hare = (row, col) != (hare_row, hare_col)
        not_stag = (row, col) != (stag_row, stag_col)
        occupied = self.grid[row][col] != AVAILABLE

        return occupied and not_hare and not_stag

    def neighboring_positions(self, curr_row: int, curr_col: int,
                              filter_availability: bool = True) -> List[Tuple[int, int]]:
        positions = []

        for movement in POSSIBLE_MOVEMENTS:
            for delta in POSSIBLE_DELTA_VALS:
                if movement == VERTICAL:
                    new_row, new_col = curr_row + delta, curr_col

                else:
                    new_row, new_col = curr_row, curr_col + delta

                if not filter_availability or self.is_available(new_row, new_col):
                    row, col = self.adjust_vals(new_row, new_col)
                    positions.append((row, col))

        return positions

    def delta_row(self, curr_row: int, new_row: int) -> int:
        move_down = (self.height - curr_row) + new_row
        move_up = curr_row + (self.height - new_row)
        move_regular = abs(curr_row - new_row)

        return min([move_down, move_up, move_regular])

    def delta_col(self, curr_col: int, new_col: int) -> int:
        move_left = (self.width - curr_col) + new_col
        move_right = curr_col + (self.width - new_col)
        move_regular = abs(curr_col - new_col)

        return min([move_left, move_right, move_regular])

    def n_movements(self, curr_row: int, curr_col: int, new_row: int, new_col: int) -> int:
        n_steps = self.delta_row(curr_row, new_row) + self.delta_col(curr_col, new_col)

        return n_steps

    def neighbors(self, row1: int, col1: int, row2: int, col2: int) -> bool:
        n_movements = self.n_movements(row1, col1, row2, col2)

        return n_movements <= MAX_MOVEMENT_UNITS

    def process_actions(self, action_map: Dict[str, Tuple[int, int]]) -> List[float]:
        for agent_name, tup in action_map.items():
            new_row, new_col = tup
            curr_row, curr_col = self.agent_positions[agent_name]
            agent_idx = self.grid[curr_row][curr_col]

            # Adjust the new row and col values so that they are on the grid (i.e. apply wrap around if we go
            # beyond the grid boundaries)
            new_row, new_col = self.adjust_vals(new_row, new_col)

            # Make sure the new row and column represent a valid movement (i.e. we can only move left, right, up, or
            # down, for a total of 1 unit of movement)
            n_movements = self.n_movements(curr_row, curr_col, new_row, new_col)
            if n_movements > MAX_MOVEMENT_UNITS:
                raise Exception(f'Cannot move from {(curr_row, curr_col)} to {(new_row, new_col)} because there are '
                                f'{n_movements} > {MAX_MOVEMENT_UNITS} movements')

            # Only move the agent if its desired new position is available
            if self.is_available(new_row, new_col):
                # The old position should now be available since the agent is moving
                self.grid[curr_row][curr_col] = AVAILABLE

                # Update the new position
                self.grid[new_row][new_col] = agent_idx
                self.agent_positions[agent_name] = (new_row, new_col)

        # Update the round number
        self.round_num += 1

        # Calculate agent rewards for this round
        rewards, hare_captured, stag_captured = [0] * len(self.agent_names), self.hare_captured(), self.stag_captured()

        if hare_captured or stag_captured:
            hare_row, hare_col = self.agent_positions[HARE_NAME]
            stag_row, stag_col = self.agent_positions[STAG_NAME]
            hare_hunters, stag_hunters = set(), set()

            # Find all the hunters that have surrounded the hare and/or stag
            for i, agent_name in enumerate(self.agent_names):
                if agent_name == HARE_NAME or agent_name == STAG_NAME:
                    continue

                row, col = self.agent_positions[agent_name]

                if self.neighbors(row, col, hare_row, hare_col):
                    hare_hunters.add(agent_name)

                if self.neighbors(row, col, stag_row, stag_col):
                    stag_hunters.add(agent_name)

            # Distribute the rewards to the hunters
            for i, agent_name in enumerate(self.agent_names):
                if hare_captured and agent_name in hare_hunters:
                    rewards[i] = HARE_REWARD / len(hare_hunters)

                if stag_captured and agent_name in stag_hunters:
                    rewards[i] = STAG_REWARD / len(stag_hunters)

        return rewards

    def hare_captured(self) -> bool:
        curr_row, curr_col = self.agent_positions[HARE_NAME]

        # Try all possible movements for the hare; if it is surrounded on the required number of sides, it is captured
        n_hunter_neighbors = 0

        for movement in POSSIBLE_MOVEMENTS:
            for delta in POSSIBLE_DELTA_VALS:
                if movement == VERTICAL:
                    new_row, new_col = curr_row + delta, curr_col

                else:
                    new_row, new_col = curr_row, curr_col + delta

                n_hunter_neighbors += 1 if self.hunter_in_position(new_row, new_col) else 0

        return n_hunter_neighbors >= N_REQUIRED_TO_CAPTURE_HARE

    def stag_captured(self) -> bool:
        curr_row, curr_col = self.agent_positions[STAG_NAME]

        # Try all possible movements for the stag; if it is surrounded on the required number of sides, it is captured
        n_hunter_neighbors = 0

        for movement in POSSIBLE_MOVEMENTS:
            for delta in POSSIBLE_DELTA_VALS:
                if movement == VERTICAL:
                    new_row, new_col = curr_row + delta, curr_col

                else:
                    new_row, new_col = curr_row, curr_col + delta

                n_hunter_neighbors += 1 if self.hunter_in_position(new_row, new_col) else 0

        return n_hunter_neighbors >= N_REQUIRED_TO_CAPTURE_STAG

    # def collective_distance(self) -> float:
    #     collective_distance, (prey_row, prey_col) = 0, self.agent_positions[Utils.PREY_NAME]
    #
    #     for agent_name, (row, col) in self.agent_positions.items():
    #         if agent_name == Utils.PREY_NAME:
    #             continue
    #
    #         dist_from_prey = self.n_movements(row, col, prey_row, prey_col)
    #         collective_distance += dist_from_prey
    #
    #     return collective_distance
    #
    # def agent_distance(self, name: str) -> float:
    #     prey_row, prey_col = self.agent_positions[Utils.PREY_NAME]
    #     row, col = self.agent_positions[name]
    #
    #     return self.n_movements(row, col, prey_row, prey_col)
