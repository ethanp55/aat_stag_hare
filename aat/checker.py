from environment.state import State
import numpy as np
from typing import List
from utils.utils import HARE_NAME, N_HUNTERS, STAG_NAME


class AssumptionChecker:
    def __init__(self, name: str) -> None:
        self.name = name

        # Progress assumption estimates
        self.width_small = 0.5
        self.width_large = 0.5
        self.height_small = 0.5
        self.height_large = 0.5
        self.i_am_closest_to_hare = 0.5
        self.i_am_closest_to_stag = 0.5
        self.others_getting_closer_to_hare = 0.0
        self.others_getting_closer_to_stag = 0.0

        # Previous values (used in estimate calculations)
        self.prev_state_dists = None
        self.prev_state_collisions = None

    def check_assumptions(self, state: State) -> None:
        pass

    def assumptions(self) -> List[float]:
        return [self.width_small, self.width_large, self.height_small, self.height_large,
                self.i_am_closest_to_hare, self.i_am_closest_to_stag, self.others_getting_closer_to_hare,
                self.others_getting_closer_to_stag]

    def _check_progress(self, state: State) -> None:
        # Check the grid sizes
        width, height = state.width, state.height
        self.width_small = width / 10 if width <= 10 else 0.0
        self.width_large = 10 / width if width > 10 else 0.0
        self.height_small = height / 10 if height <= 10 else 0.0
        self.height_large = 10 / height if height > 10 else 0.0

        # Check how close we are to the stag and hare, relative to the other hunters
        stag_row, stag_col = state.agent_positions[STAG_NAME]
        hare_row, hare_col = state.agent_positions[HARE_NAME]
        curr_row, curr_col = state.agent_positions[self.name]
        stag_dist = state.n_movements(curr_row, curr_col, stag_row, stag_col)
        hare_dist = state.n_movements(curr_row, curr_col, hare_row, hare_col)

        smallest_dist_to_hare, smallest_dist_to_stag = np.inf, np.inf

        for agent_name, (row, col) in state.agent_positions.items():
            if agent_name == HARE_NAME or agent_name == STAG_NAME:
                continue

            dist_to_stag = state.n_movements(row, col, stag_row, stag_col)
            dist_to_hare = state.n_movements(row, col, hare_row, hare_col)
            smallest_dist_to_hare = min(smallest_dist_to_hare, dist_to_hare)
            smallest_dist_to_stag = min(smallest_dist_to_stag, dist_to_stag)

        self.i_am_closest_to_hare = smallest_dist_to_hare / hare_dist
        self.i_am_closest_to_stag = smallest_dist_to_stag / stag_dist

        # Check if the other hunters are getting closer to the hare and/or stag
        if self.prev_state_dists is not None:
            n_getting_closer_to_hare, n_getting_closer_to_stag, n_other_hunters = 0, 0, N_HUNTERS - 1
            prev_stag_row, prev_stag_col = self.prev_state_dists.agent_positions[STAG_NAME]
            prev_hare_row, prev_hare_col = self.prev_state_dists.agent_positions[HARE_NAME]

            for agent_name, (prev_row, prev_col) in self.prev_state_dists.agent_positions.items():
                if agent_name == HARE_NAME or agent_name == STAG_NAME or agent_name == self.name:
                    continue

                curr_row, curr_col = state.agent_positions[agent_name]

                prev_stag_dist = self.prev_state_dists.n_movements(prev_row, prev_col, prev_stag_row, prev_stag_col)
                prev_hare_dist = self.prev_state_dists.n_movements(prev_row, prev_col, prev_hare_row, prev_hare_col)
                stag_dist = state.n_movements(curr_row, curr_col, stag_row, stag_col)
                hare_dist = state.n_movements(curr_row, curr_col, hare_row, hare_col)

                n_getting_closer_to_stag += 1 if stag_dist < prev_stag_dist else 0
                n_getting_closer_to_hare += 1 if hare_dist < prev_hare_dist else 0

            self.others_getting_closer_to_hare = n_getting_closer_to_hare / n_other_hunters
            self.others_getting_closer_to_stag = n_getting_closer_to_stag / n_other_hunters

        self.prev_state_dists = state

    def _check_collisions(self, state: State, target: str) -> float:
        if self.prev_state_collisions is not None:
            n_collisions, (prey_row, prey_col) = 0, state.agent_positions[target]

            for agent_name, (prev_row, prev_col) in self.prev_state_collisions.agent_positions.items():
                if agent_name == HARE_NAME or agent_name == STAG_NAME:
                    continue

                curr_row, curr_col = state.agent_positions[agent_name]

                # If the agent couldn't/didn't move and it is not currently next to the prey, there was likely a
                # collision
                if (prev_row, prev_col) == (curr_row, curr_col) and not \
                        state.neighbors(curr_row, curr_col, prey_row, prey_col):
                    n_collisions += 1

        else:
            n_collisions = 0

        self.prev_state_collisions = state

        return n_collisions


class TeamAwareChecker(AssumptionChecker):
    def __init__(self, name: str) -> None:
        AssumptionChecker.__init__(self, name)

        # Assumption estimates
        self.getting_closer_to_stag = 0.0
        self.no_collisions = 1.0

        # Previous values (used in estimate calculations)
        self.prev_dist_to_stag = None

    def check_assumptions(self, state: State) -> None:
        # Check if we're getting closer to the stag
        stag_row, stag_col = state.agent_positions[STAG_NAME]
        curr_row, curr_col = state.agent_positions[self.name]
        dist = state.n_movements(curr_row, curr_col, stag_row, stag_col)
        if self.prev_dist_to_stag is not None:
            self.getting_closer_to_stag = 1.0 if dist < self.prev_dist_to_stag else \
                (0.5 if dist == self.prev_dist_to_stag else 0.0)
        self.prev_dist_to_stag = dist

        # Check if there were collisions
        n_collisions = self._check_collisions(state, STAG_NAME)
        self.no_collisions = 1 - (n_collisions / N_HUNTERS)

        # Check progress
        self._check_progress(state)

    def assumptions(self) -> List[float]:
        return [self.getting_closer_to_stag, self.no_collisions] + AssumptionChecker.assumptions(self)


class GreedyPlannerStagChecker(AssumptionChecker):
    def __init__(self, name: str) -> None:
        AssumptionChecker.__init__(self, name)

        # Assumption estimates
        self.getting_closer_to_stag = 0.0
        self.no_collisions = 1.0

        # Previous values (used in estimate calculations)
        self.prev_dist_to_stag = None

    def check_assumptions(self, state: State) -> None:
        # Check if we're getting closer to the stag
        stag_row, stag_col = state.agent_positions[STAG_NAME]
        curr_row, curr_col = state.agent_positions[self.name]
        dist = state.n_movements(curr_row, curr_col, stag_row, stag_col)
        if self.prev_dist_to_stag is not None:
            self.getting_closer_to_stag = 1.0 if dist < self.prev_dist_to_stag else \
                (0.5 if dist == self.prev_dist_to_stag else 0.0)
        self.prev_dist_to_stag = dist

        # Check if there were collisions
        n_collisions = self._check_collisions(state, STAG_NAME)
        self.no_collisions = 1 - (n_collisions / N_HUNTERS)

        # Check progress
        self._check_progress(state)

    def assumptions(self) -> List[float]:
        return [self.getting_closer_to_stag, self.no_collisions] + AssumptionChecker.assumptions(self)


class GreedyHareChecker(AssumptionChecker):
    def __init__(self, name: str) -> None:
        AssumptionChecker.__init__(self, name)

        # Assumption estimates
        self.getting_closer_to_hare = 0.0

        # Previous values (used in estimate calculations)
        self.prev_dist_to_hare = None

    def check_assumptions(self, state: State) -> None:
        # Check if we're getting closer to the hare
        hare_row, hare_col = state.agent_positions[HARE_NAME]
        curr_row, curr_col = state.agent_positions[self.name]
        dist = state.n_movements(curr_row, curr_col, hare_row, hare_col)
        if self.prev_dist_to_hare is not None:
            self.getting_closer_to_hare = 1.0 if dist < self.prev_dist_to_hare else \
                (0.5 if dist == self.prev_dist_to_hare else 0.0)
        self.prev_dist_to_hare = dist

        # Check progress
        self._check_progress(state)

    def assumptions(self) -> List[float]:
        return [self.getting_closer_to_hare] + AssumptionChecker.assumptions(self)


class GreedyPlannerHareChecker(AssumptionChecker):
    def __init__(self, name: str) -> None:
        AssumptionChecker.__init__(self, name)

        # Assumption estimates
        self.getting_closer_to_hare = 0.0

        # Previous values (used in estimate calculations)
        self.prev_dist_to_hare = None

    def check_assumptions(self, state: State) -> None:
        # Check if we're getting closer to the hare
        hare_row, hare_col = state.agent_positions[HARE_NAME]
        curr_row, curr_col = state.agent_positions[self.name]
        dist = state.n_movements(curr_row, curr_col, hare_row, hare_col)
        if self.prev_dist_to_hare is not None:
            self.getting_closer_to_hare = 1.0 if dist < self.prev_dist_to_hare else \
                (0.5 if dist == self.prev_dist_to_hare else 0.0)
        self.prev_dist_to_hare = dist

        # Check progress
        self._check_progress(state)

    def assumptions(self) -> List[float]:
        return [self.getting_closer_to_hare] + AssumptionChecker.assumptions(self)

