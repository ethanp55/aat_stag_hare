from agents.alegaatr import AlegAATr
from agents.aleqgaatr import AleqgAATr
from agents.dqn import DQNAgent
from agents.generator import GreedyHareGen
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
import numpy as np
import os
from utils.utils import N_HUNTERS


N_EPOCHS = 30
GRID_SIZE = (15, 15)
n_other_hunters = N_HUNTERS - 1

names = ['DQN', 'MADQN', 'RDQN', 'AleqgAATr', 'RAlegAATr', 'SOAleqgAATr', 'AlegAATr', 'SMAlegAATr', 'QAlegAATr',
         'RawO', 'PPO', 'RAAT']

# Reset any existing simulation files (opening a file in write mode will truncate it)
for file in os.listdir('../simulations/adaptability_results/'):
    name = file.split('_')[0]
    if name in names:
        # if True:
        with open(f'../simulations/adaptability_results/{file}', 'w', newline='') as _:
            pass

# Run the training process
for epoch in range(N_EPOCHS):
    print(f'Epoch {epoch + 1}')
    height, width = GRID_SIZE

    list_of_other_hunters = []
    list_of_other_hunters.append(([GreedyHareGen(f'GreedyHareGen{i}') for i in range(n_other_hunters)], 'greedyhare'))
    list_of_other_hunters.append((None, 'selfplay'))

    for other_hunters, label in list_of_other_hunters:
        agents_to_test = []
        agents_to_test.append(DQNAgent())
        agents_to_test.append(AlegAATr(lmbda=0.0, ml_model_type='knn', enhanced=True))
        agents_to_test.append(AleqgAATr())
        agents_to_test.append(MADQN())
        agents_to_test.append(SOAleqgAATr())
        agents_to_test.append(SMAlegAATr())
        agents_to_test.append(RAlegAATr())
        agents_to_test.append(RDQN())
        agents_to_test.append(PPO())
        agents_to_test.append(QAlegAATr(enhanced=True))
        agents_to_test.append(RawO(enhanced=True))
        agents_to_test.append(RAAT())

        self_play_agents = []
        self_play_agents.append([DQNAgent(f'DQN{i}') for i in range(n_other_hunters)])
        self_play_agents.append([AlegAATr(f'AlegAATr{i}', lmbda=0.0, ml_model_type='knn', enhanced=True) for i in range(n_other_hunters)])
        self_play_agents.append([AleqgAATr(f'AleqgAATr{i}') for i in range(n_other_hunters)])
        self_play_agents.append([MADQN(f'MADQN{i}') for i in range(n_other_hunters)])
        self_play_agents.append([SOAleqgAATr(f'SOAleqgAATr{i}') for i in range(n_other_hunters)])
        self_play_agents.append([SMAlegAATr(f'SMAlegAATr{i}') for i in range(n_other_hunters)])
        self_play_agents.append([RAlegAATr(f'RAlegAATr{i}') for i in range(n_other_hunters)])
        self_play_agents.append([RDQN(f'RDQN{i}') for i in range(n_other_hunters)])
        self_play_agents.append([PPO(f'PPO{i}') for i in range(n_other_hunters)])
        self_play_agents.append([QAlegAATr(f'QAlegAATr{i}', enhanced=True) for i in range(n_other_hunters)])
        self_play_agents.append([RawO(f'RawO{i}', enhanced=True) for i in range(n_other_hunters)])
        self_play_agents.append([RAAT(f'RAAT{i}') for i in range(n_other_hunters)])

        for i, agent_to_test in enumerate(agents_to_test):
            if label == 'selfplay':
                assert other_hunters is None
                assert len(self_play_agents[i]) == n_other_hunters
                hunters = deepcopy(self_play_agents[i])
                for hunter in hunters:
                    assert isinstance(hunter, type(agent_to_test))
            else:
                assert len(other_hunters) == n_other_hunters
                hunters = deepcopy(other_hunters)
            hunters.append(agent_to_test)
            assert len(hunters) == N_HUNTERS
            sim_label = f'{agent_to_test.name}_{label}_h={height}_w={width}'
            run(hunters, height, width, results_file=f'../simulations/adaptability_results/{sim_label}.csv')

# Coop
for epoch in range(N_EPOCHS):
    print(f'Epoch {epoch + 1}')
    height, width = GRID_SIZE

    cooperators = [RAAT('RAAT1'), RAAT('RAAT2'),
                   QAlegAATr('QAlegAATr1', enhanced=True), QAlegAATr('QAlegAATr2', enhanced=True),
                   AlegAATr('AlegAATr1', lmbda=0.0, ml_model_type='knn', enhanced=True),
                   AlegAATr('AlegAATr2', lmbda=0.0, ml_model_type='knn', enhanced=True)]

    agents_to_test = []
    agents_to_test.append(DQNAgent())
    agents_to_test.append(AlegAATr(lmbda=0.0, ml_model_type='knn', enhanced=True))
    agents_to_test.append(AleqgAATr())
    agents_to_test.append(MADQN())
    agents_to_test.append(SOAleqgAATr())
    agents_to_test.append(SMAlegAATr())
    agents_to_test.append(RAlegAATr())
    agents_to_test.append(RDQN())
    agents_to_test.append(PPO())
    agents_to_test.append(QAlegAATr(enhanced=True))
    agents_to_test.append(RawO(enhanced=True))
    agents_to_test.append(RAAT())

    for agent_to_test in agents_to_test:
        while True:
            hunter_indices = np.random.choice(len(cooperators), n_other_hunters, replace=False)
            hunters = [deepcopy(cooperators[idx]) for idx in hunter_indices]

            if not isinstance(hunters[0], type(agent_to_test)) and not isinstance(hunters[1], type(agent_to_test)):
                break

        hunters.append(agent_to_test)
        assert len(hunters) == N_HUNTERS
        sim_label = f'{agent_to_test.name}_coop_h={height}_w={width}'
        run(hunters, height, width, results_file=f'../simulations/adaptability_results/{sim_label}.csv')
