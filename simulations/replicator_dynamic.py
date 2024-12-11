from agents.agent import Agent
from agents.dqn import DQNAgent
from agents.alegaatr import AlegAATr
from agents.aleqgaatr import AleqgAATr
from agents.madqn import MADQN
from agents.ppo import PPO
from agents.qalegaatr import QAlegAATr
from agents.raat import RAAT
from agents.ralegaatr import RAlegAATr
from agents.rawo import RawO
from agents.rdqn import RDQN
from agents.smalegaatr import SMAlegAATr
from agents.soaleqgaatr import SOAleqgAATr
from copy import deepcopy
from environment.runner import run
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import List
from utils.utils import N_HUNTERS


def _get_other_hunters(pop_selection: List[List[Agent]], frequencies: List[float]) -> List[Agent]:
    h1_idx = np.random.choice(N_AGENTS, p=frequencies)
    h2_idx = np.random.choice(N_AGENTS, p=frequencies)

    if h1_idx == h2_idx:
        return pop_selection[h1_idx]

    return [pop_selection[h1_idx][0], pop_selection[h2_idx][0]]


# Variables
N_ITERATIONS = 100
GRID_SIZE = (11, 11)
progress_percentage_chunk = int(0.05 * N_ITERATIONS)
n_other_hunters = N_HUNTERS - 1

# Frequencies and population details
algorithms = [
    DQNAgent(),
    # MADQN(),
    # RDQN(),
    AleqgAATr(),
    RAlegAATr(),
    # SOAleqgAATr(),
    AlegAATr(lmbda=0.0, ml_model_type='knn', enhanced=True),
    # SMAlegAATr(enhanced=False),
    QAlegAATr(enhanced=True),
    RawO(enhanced=True),
    # PPO(),
    RAAT(enhanced=False)
]
algorithms2 = [
    DQNAgent('DQN1'),
    # MADQN(),
    # RDQN(),
    AleqgAATr('AleqgAATr1'),
    RAlegAATr('RAlegAATr1'),
    # SOAleqgAATr(),
    AlegAATr('AlegAATr1', lmbda=0.0, ml_model_type='knn', enhanced=True),
    # SMAlegAATr(enhanced=False),
    QAlegAATr('QAlegAATr1', enhanced=True),
    RawO('RawO1', enhanced=True),
    # PPO(),
    RAAT('RAAT1', enhanced=False)
]
algorithms3 = [
    DQNAgent('DQN2'),
    # MADQN(),
    # RDQN(),
    AleqgAATr('AleqgAATr2'),
    RAlegAATr('RAlegAATr2'),
    # SOAleqgAATr(),
    AlegAATr('AlegAATr2', lmbda=0.0, ml_model_type='knn', enhanced=True),
    # SMAlegAATr(enhanced=False),
    QAlegAATr('QAlegAATr2', enhanced=True),
    RawO('RawO2', enhanced=True),
    # PPO(),
    RAAT('RAAT2', enhanced=False)
]
N_AGENTS = len(algorithms)

R = np.zeros((N_AGENTS, N_AGENTS, N_AGENTS))
for i, alg1 in enumerate(algorithms):
    print(f'Agent {i}')
    for j, alg2 in enumerate(algorithms2):
        for k, alg3 in enumerate(algorithms3):
            rewards_j_k = []
            # for _ in range(N_ITERATIONS):
            for _ in range(2):
                hunters = [deepcopy(alg2), deepcopy(alg3), deepcopy(alg1)]
                rewards = run(hunters, *GRID_SIZE)
                rewards_j_k.append(rewards[-1])
            R[i][j][k] = sum(rewards_j_k) / len(rewards_j_k)
# for j in range(len(algorithms2)):
#     for k in range(len(algorithms3)):
#         R[:, j, k] = MinMaxScaler().fit_transform(R[:, j, k].reshape(-1, 1)).reshape(-1,)
min_r, max_r = R.min(), R.max()
R = (R - min_r) / (max_r - min_r)
print(R)

# R = MinMaxScaler().fit_transform(R)
# assert R.min() == 0 and R.max() == 1


# Used for ensuring that the agent frequencies compose a valid probability distribution
def convert_to_probs(values: List[float]) -> List[float]:
    shift_values = values - np.min(values)
    exp_values = np.exp(shift_values)
    probabilities = exp_values / np.sum(exp_values)

    return list(probabilities)


for include_alegaatr in [True, False]:
    if include_alegaatr:
        agent_frequencies = [1 / N_AGENTS] * N_AGENTS
        agent_representation_over_time = {agent.name: [1 / N_AGENTS] for agent in algorithms}
    else:
        agent_frequencies = [1 / (N_AGENTS - 1)] * N_AGENTS
        agent_frequencies[3] = 0
        agent_representation_over_time = {agent.name: [1 / (N_AGENTS - 1)] for agent in algorithms}
        agent_representation_over_time['AlegAATr'] = [0]

    for iteration in range(N_ITERATIONS):
        fitnesses = []
        for i, alg in enumerate(algorithms):
            if not include_alegaatr and alg.name == 'AlegAATr':
                fitnesses.append(0)
                continue
            fitness = 0
            for j, alg2 in enumerate(algorithms2):
                if not include_alegaatr and alg2.name == 'AlegAATr':
                    continue
                for k, alg3 in enumerate(algorithms3):
                    if not include_alegaatr and alg3.name == 'AlegAATr':
                        continue
                    fitness += R[i][j][k] * agent_frequencies[j] * agent_frequencies[k]
            fitnesses.append(fitness)

        avg_fitness = 0
        for i, alg in enumerate(algorithms):
            avg_fitness += agent_frequencies[i] * fitnesses[i]
        for i, alg in enumerate(algorithms):
            agent_frequencies[i] += agent_frequencies[i] * (fitnesses[i] - avg_fitness)
        # agent_frequencies = convert_to_probs(agent_frequencies)
        print(sum(agent_frequencies))
        # assert round(sum(agent_frequencies), 3) == 1

        # Update data for plot
        for i, alg in enumerate(algorithms):
            new_proportion = agent_frequencies[i]
            agent_representation_over_time[alg.name] += [new_proportion]

    # Plot agent representations over time
    colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'magenta', 'lime', 'pink', 'yellow', 'brown', 'black']
    name_conversions = {
        'DQN': 'DQN',
        'MADQN': 'MADQN',
        'RDQN': 'RDQN',
        'AleqgAATr': 'TRawAAT',
        'RAlegAATr': 'TAAT',
        'SOAleqgAATr': 'STRawAAT',
        'AlegAATr': 'AlegAATr',
        'SMAlegAATr': 'SRRawAAT',
        'QAlegAATr': 'RRawAAT',
        'RawO': 'RawR',
        'PPO': 'PPO',
        'RAAT': 'RAAT'
    }
    plt.figure(figsize=(10, 3))
    plt.grid()
    for i, agent in enumerate(agent_representation_over_time.keys()):
        if not include_alegaatr and agent == 'AlegAATr':
            continue
        proportions, color = agent_representation_over_time[agent], colors[i]
        plt.plot(proportions, label=name_conversions[agent], color=color)
    plt.xlabel('Iteration', fontsize=18, fontweight='bold')
    plt.ylabel('Proportion', fontsize=18, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.savefig(f'../simulations/replicator_dynamic_{include_alegaatr}.png', bbox_inches='tight')
    plt.clf()
