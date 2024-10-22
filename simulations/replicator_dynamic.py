from agents.dqn import DQNAgent
from agents.alegaatr import AlegAATr
from agents.aleqgaatr import AleqgAATr
from agents.madqn import MADQN
from agents.ppo import PPO
from agents.qalegaatr import QAlegAATr
from agents.ralegaatr import RAlegAATr
from agents.rawo import RawO
from agents.rdqn import RDQN
from agents.smalegaatr import SMAlegAATr
from agents.soaleqgaatr import SOAleqgAATr
from copy import deepcopy
from environment.runner import run
import numpy as np
from typing import List
from utils.utils import N_HUNTERS


# Variables
N_AGENTS = 11
N_ITERATIONS = 500
GRID_SIZE = (11, 11)
progress_percentage_chunk = int(0.05 * N_ITERATIONS)
n_other_hunters = N_HUNTERS - 1

# Frequencies and population details
agent_frequencies = [1 / N_AGENTS] * N_AGENTS
algorithms = [
    DQNAgent(),
    MADQN(),
    RDQN(),
    AleqgAATr(),
    RAlegAATr(),
    SOAleqgAATr(),
    AlegAATr(lmbda=0.0, ml_model_type='knn', enhanced=True),
    SMAlegAATr(enhanced=False),
    QAlegAATr(enhanced=True),
    RawO(enhanced=True),
    PPO()
]
population_selection = [
    [DQNAgent(f'DQN{i}') for i in range(n_other_hunters)],
    [MADQN(f'MADQN{i}') for i in range(n_other_hunters)],
    [RDQN(f'RDQN{i}') for i in range(n_other_hunters)],
    [AleqgAATr(f'AleqgAATr{i}') for i in range(n_other_hunters)],
    [RAlegAATr(f'RAlegAATr{i}') for i in range(n_other_hunters)],
    [SOAleqgAATr(f'SOAleqgAATr{i}') for i in range(n_other_hunters)],
    [AlegAATr(f'AlegAATr{i}', lmbda=0.0, ml_model_type='knn', enhanced=True) for i in range(n_other_hunters)],
    [SMAlegAATr(f'SMAlegAATr{i}', enhanced=False) for i in range(n_other_hunters)],
    [QAlegAATr(f'QAlegAATr{i}', enhanced=True) for i in range(n_other_hunters)],
    [RawO(f'RawO{i}', enhanced=True) for i in range(n_other_hunters)],
    [PPO(f'PPO{i}') for i in range(n_other_hunters)]
]
population = [population_selection[i] for i in range(N_AGENTS)]
population_types = [type(hunters[0]) for hunters in population]


# Used for ensuring that the agent frequencies compose a valid probability distribution
def convert_to_probs(values: List[float]) -> List[float]:
    shift_values = values - np.min(values)
    exp_values = np.exp(shift_values)
    probabilities = exp_values / np.sum(exp_values)

    return list(probabilities)


for iteration in range(N_ITERATIONS):
    # Progress report
    curr_iteration = iteration + 1
    if curr_iteration != 0 and progress_percentage_chunk != 0 and curr_iteration % progress_percentage_chunk == 0:
        print(f'{100 * (curr_iteration / N_ITERATIONS)}%')

    # Rewards for this iteration
    agent_rewards, population_rewards = [0] * N_AGENTS, []

    # Test each algorithm against every algorithm in the population (allows algorithms to re-enter the population)
    for i, alg in enumerate(algorithms):
        for other_hunters in population:
            # Values needed for the simulation - copy each agent to make sure none of the parameters get messed up
            agent = deepcopy(alg)
            hunters = deepcopy(other_hunters)
            hunters.append(agent)

            # Run the simulation, extract the rewards
            final_rewards = run(hunters, *GRID_SIZE)

            # Update the agent's reward
            agent_reward = final_rewards[-1]
            agent_rewards[i] += agent_reward

            # If the agent is in the population, update the population rewards
            if type(agent) in population_types:
                population_rewards.append(final_rewards[-1])

    # Update each algorithm's frequency/probability of being added to the population
    avg_pop_reward = sum(population_rewards) / len(population_rewards)
    for i in range(len(agent_frequencies)):
        avg_agent_reward = agent_rewards[i] / len(population)
        freq_update = agent_frequencies[i] * (avg_agent_reward - avg_pop_reward)
        agent_frequencies[i] += freq_update
    agent_frequencies = convert_to_probs(agent_frequencies)  # Ensure the frequencies are a valid distribution
    population_indices = np.random.choice(N_AGENTS, N_AGENTS, p=agent_frequencies)
    population = [population_selection[i] for i in population_indices]
    population_types = [type(hunters[0]) for hunters in population]

    # Status update on the population
    print([hunters[0].name[:-1] for hunters in population])
