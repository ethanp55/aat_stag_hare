from agents.agent import Agent
from agents.alegaatr import AlegAATr
from agents.generator_pool import GeneratorPool
from agents.greedy import Greedy
from agents.qalegaatr import QAlegAATr
from agents.raat import RAAT
from agents.rawo import RawO
from agents.smalegaatr import SMAlegAATr
from agents.team_aware import TeamAware
from copy import deepcopy
from environment.runner import run
from environment.state import State
import numpy as np
import os
from typing import Tuple
from utils.utils import HARE_NAME, N_HUNTERS


# ----------------------------------------------------------------------------------------------------------------------
# Agents used to select generators (for training purposes) -------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# Agent that just randomly (uniform) chooses a generator to use
class UniformSelector(Agent):
    def __init__(self, name: str = 'UniformSelector', check_assumptions: bool = False,
                 no_baseline: bool = False) -> None:
        Agent.__init__(self, name)
        self.generator_pool = GeneratorPool(name, check_assumptions=check_assumptions, no_baseline_labels=no_baseline)
        self.check_assumptions = check_assumptions
        self.generator_indices = [i for i in range(len(self.generator_pool.generators))]
        self.generator_to_use_idx = None

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        # Get the actions of every generator
        generator_to_token_allocs = self.generator_pool.act(state, reward, round_num, self.generator_to_use_idx)

        # Randomly (uniform) choose a generator to use
        self.generator_to_use_idx = np.random.choice(self.generator_indices)

        token_allocations = generator_to_token_allocs[self.generator_to_use_idx]

        # If we're done and are supposed to train AAT, do so
        if (state.hare_captured() or state.stag_captured()) and self.check_assumptions:
            self.generator_pool.train_aat()

        return token_allocations


# Agent that favors generators that have been used more recently
class FavorMoreRecent(Agent):
    def __init__(self, name: str = 'FavorMoreRecent', check_assumptions: bool = False,
                 no_baseline: bool = False) -> None:
        Agent.__init__(self, name)
        self.generator_pool = GeneratorPool(name, check_assumptions=check_assumptions, no_baseline_labels=no_baseline)
        self.check_assumptions = check_assumptions
        self.generator_indices = [i for i in range(len(self.generator_pool.generators))]
        self.generator_to_use_idx, self.prev_generator_idx = None, None
        self.n_rounds_since_last_use = {}
        self.max_in_a_row = 5
        self.n_rounds_used = 0

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        # Get the actions of every generator
        generator_to_token_allocs = self.generator_pool.act(state, reward, round_num, self.generator_to_use_idx)

        # Randomly choose a generator, but favor those that have been used most recently
        rounds_since_used = [1 / self.n_rounds_since_last_use.get(i, 1) for i in self.generator_indices]
        if self.prev_generator_idx is not None and self.prev_generator_idx == self.generator_to_use_idx and \
                self.n_rounds_used >= self.max_in_a_row:
            rounds_since_used[self.generator_to_use_idx] = 0
            self.n_rounds_used = 0
        sum_val = sum(rounds_since_used)

        probabilities = [x / sum_val for x in rounds_since_used]
        self.prev_generator_idx = self.generator_to_use_idx
        self.generator_to_use_idx = np.random.choice(self.generator_indices, p=probabilities)

        # Update the number of rounds since each generator was used
        for i in self.generator_indices:
            self.n_rounds_since_last_use[i] = (
                    self.n_rounds_since_last_use.get(i, 1) + 1) if i != self.generator_to_use_idx else 1

        self.n_rounds_used += 1

        token_allocations = generator_to_token_allocs[self.generator_to_use_idx]

        # If we're done and are supposed to train AAT, do so
        if (state.hare_captured() or state.stag_captured()) and self.check_assumptions:
            self.generator_pool.train_aat()

        return token_allocations


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

N_EPOCHS = 10
GRID_SIZES = [(10, 10), (13, 13)]
NO_BASELINE = False


def run_training():
    # Variables to track progress
    n_training_iterations = N_EPOCHS * len(GRID_SIZES)
    progress_percentage_chunk = int(0.05 * n_training_iterations)
    curr_iteration = 0
    print(n_training_iterations, progress_percentage_chunk)
    n_other_hunters = N_HUNTERS - 1

    # Reset any existing training files (opening a file in write mode will truncate it)
    for file in os.listdir('../aat/training_data/'):
        if (NO_BASELINE and 'sin_c' in file) or (not NO_BASELINE and 'sin_c' not in file):
            with open(f'../aat/training_data/{file}', 'w', newline='') as _:
                pass

    # Run the training process
    for epoch in range(N_EPOCHS):
        print(f'Epoch {epoch + 1}')

        for height, width in GRID_SIZES:
            if curr_iteration != 0 and curr_iteration % progress_percentage_chunk == 0:
                print(f'{100 * (curr_iteration / n_training_iterations)}%')

            list_of_other_hunters = []
            list_of_other_hunters.append([TeamAware(f'TeamAware{i}') for i in range(n_other_hunters)])
            list_of_other_hunters.append([Greedy(f'Greedy{i}', HARE_NAME) for i in range(n_other_hunters)])
            list_of_other_hunters.append([FavorMoreRecent(f'FavorMoreRecentTrain{i}') for i in range(n_other_hunters)])

            for other_hunters in list_of_other_hunters:
                assert len(other_hunters) == n_other_hunters
                agents_to_train_on = []
                # agents_to_train_on.append(UniformSelector(check_assumptions=True, no_baseline=NO_BASELINE))
                # agents_to_train_on.append(FavorMoreRecent(check_assumptions=True, no_baseline=NO_BASELINE))
                # agents_to_train_on.append(SMAlegAATr(train=True))
                agents_to_train_on.append(AlegAATr(lmbda=0.0, ml_model_type='knn', train=True))
                # agents_to_train_on.append(QAlegAATr(train=True))
                # agents_to_train_on.append(RawO(train=True))
                # agents_to_train_on.append(RAAT(train=True))

                for agent_to_train_on in agents_to_train_on:
                    hunters = deepcopy(other_hunters)
                    hunters.append(agent_to_train_on)
                    assert len(hunters) == N_HUNTERS
                    run(hunters, height, width)

            curr_iteration += 1


if __name__ == '__main__':
    run_training()
