from agents.generator_pool import GeneratorPool
from copy import deepcopy
from environment.runner import run
import numpy as np
import os
from simple_rl.agents.AgentClass import Agent
from simple_rl.mdp.markov_game.MarkovGameMDPClass import MarkovGameMDP


# ----------------------------------------------------------------------------------------------------------------------
# Agents used to select generators (for training purposes) -------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# Agent that just randomly (uniform) chooses a generator to use
class UniformSelector(Agent):
    def __init__(self, game: MarkovGameMDP, player: int, check_assumptions: bool = False,
                 no_baseline: bool = False) -> None:
        Agent.__init__(self, name='UniformSelector', actions=[])
        self.player = player
        self.generator_pool = GeneratorPool('pool', game, player, check_assumptions=check_assumptions,
                                            no_baseline_labels=no_baseline)
        self.check_assumptions = check_assumptions
        self.generator_indices = [i for i in range(len(self.generator_pool.generators))]
        self.generator_to_use_idx = None

    def store_terminal_state(self, state, reward) -> None:
        if self.check_assumptions:
            self.generator_pool.store_terminal_state(state, reward, self.generator_to_use_idx)

    def record_final_results(self, state, agent_reward) -> None:
        if self.check_assumptions:
            self.generator_pool.train_aat(state, agent_reward, self.generator_to_use_idx)

    def act(self, state, reward, round_num):
        # Get the actions of every generator
        generator_to_token_allocs = self.generator_pool.act(state, reward, round_num)

        # Randomly (uniform) choose a generator to use
        self.generator_to_use_idx = np.random.choice(self.generator_indices)

        token_allocations = generator_to_token_allocs[self.generator_to_use_idx]

        return token_allocations


# Agent that favors generators that have been used more recently
class FavorMoreRecent(Agent):
    def __init__(self, game: MarkovGameMDP, player: int, check_assumptions: bool = False,
                 no_baseline: bool = False) -> None:
        Agent.__init__(self, name='FavorMoreRecent', actions=[])
        self.player = player
        self.generator_pool = GeneratorPool('pool', game, player, check_assumptions=check_assumptions,
                                            no_baseline_labels=no_baseline)
        self.check_assumptions = check_assumptions
        self.generator_indices = [i for i in range(len(self.generator_pool.generators))]
        self.generator_to_use_idx, self.prev_generator_idx = None, None
        self.n_rounds_since_last_use = {}
        self.max_in_a_row = 5
        self.n_rounds_used = 0

    def store_terminal_state(self, state, reward) -> None:
        if self.check_assumptions:
            self.generator_pool.store_terminal_state(state, reward, self.generator_to_use_idx)

    def record_final_results(self, state, agent_reward) -> None:
        if self.check_assumptions:
            self.generator_pool.train_aat(state, agent_reward, self.generator_to_use_idx)

    def act(self, state, reward, round_num):
        # Get the actions of every generator
        generator_to_token_allocs = self.generator_pool.act(state, reward, round_num)

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

        return token_allocations


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

N_EPOCHS = 10
N_ROUNDS = [20, 30, 40, 50]
NO_BASELINE = True

# Variables to track progress
n_training_iterations = N_EPOCHS * len(N_ROUNDS)
progress_percentage_chunk = int(0.05 * n_training_iterations)
curr_iteration = 0
print(n_training_iterations, progress_percentage_chunk)

# Reset any existing training files (opening a file in write mode will truncate it)
for file in os.listdir('../aat/training_data/'):
    if (NO_BASELINE and 'sin_c' in file) or (not NO_BASELINE and 'sin_c' not in file):
        with open(f'../aat/training_data/{file}', 'w', newline='') as _:
            pass


# Run the training process
for epoch in range(N_EPOCHS):
    print(f'Epoch {epoch + 1}')
    player_idx = 1
    opp_idx = 0

    for n_rounds in N_ROUNDS:
        if curr_iteration != 0 and curr_iteration % progress_percentage_chunk == 0:
            print(f'{100 * (curr_iteration / n_training_iterations)}%')

        game = PrisonersDilemma()

        list_of_opponents = []
        list_of_opponents.append(SPP('SPP', game, opp_idx))
        list_of_opponents.append(BBL('BBL', game, opp_idx))
        list_of_opponents.append(EEE('EEE', game, opp_idx))

        for opponent in list_of_opponents:
            agents_to_train_on = []
            # agents_to_train_on.append(UniformSelector(game, player_idx, check_assumptions=True,
            #                                           no_baseline=NO_BASELINE))
            # agents_to_train_on.append(FavorMoreRecent(game, player_idx, check_assumptions=True,
            #                                           no_baseline=NO_BASELINE))
            # agents_to_train_on.append(AlegAATr(game, player_idx, lmbda=0.0, ml_model_type='knn', train=True))
            # agents_to_train_on.append(SMAlegAATr(game, player_idx, train=True))
            # agents_to_train_on.append(QAlegAATr(game, player_idx, train=True))
            agents_to_train_on.append(RawO(game, player_idx, train=True))

            for agent_to_train_on in agents_to_train_on:
                players = [deepcopy(opponent), agent_to_train_on]
                player_indices = [opp_idx, player_idx]
                run_with_specified_agents(players, player_indices, n_rounds)

        curr_iteration += 1
