from agents.alegaatr import AlegAATr
from agents.aleqgaatr import AleqgAATr
from agents.dqn import DQNAgent
from agents.egaatknn import EGAATKNN
from agents.generator import GreedyHareGen
from agents.greedy import Greedy
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
from utils.utils import N_HUNTERS, STAG_NAME


N_EPOCHS = 30
GRID_SIZE = (15, 15)
n_other_hunters = N_HUNTERS - 1

# names = ['DQN', 'MADQN', 'RDQN', 'AleqgAATr', 'RAlegAATr', 'SOAleqgAATr', 'AlegAATr', 'SMAlegAATr', 'QAlegAATr',
#          'RawO', 'PPO', 'RAAT']
#
# # Reset any existing simulation files (opening a file in write mode will truncate it)
# for file in os.listdir('../simulations/adaptability_results/'):
#     name = file.split('_')[0]
#     if name in names:
#         # if True:
#         with open(f'../simulations/adaptability_results/{file}', 'w', newline='') as _:
#             pass


def adaptability(epoch_number):
    # Defect and self-play
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
            # agents_to_test.append(EGAATKNN())
            agents_to_test.append(AleqgAATr())
            # agents_to_test.append(MADQN())
            # agents_to_test.append(SOAleqgAATr())
            # agents_to_test.append(SMAlegAATr())
            agents_to_test.append(RAlegAATr())
            # agents_to_test.append(RDQN())
            # agents_to_test.append(PPO())
            agents_to_test.append(QAlegAATr(enhanced=True))
            agents_to_test.append(RawO(enhanced=True))
            agents_to_test.append(RAAT(enhanced=True))

            self_play_agents = []
            self_play_agents.append([DQNAgent(f'DQN{i}') for i in range(n_other_hunters)])
            self_play_agents.append([AlegAATr(f'AlegAATr{i}', lmbda=0.0, ml_model_type='knn', enhanced=True) for i in range(n_other_hunters)])
            # self_play_agents.append([EGAATKNN(f'EGAATKNN{i}') for i in range(n_other_hunters)])
            self_play_agents.append([AleqgAATr(f'AleqgAATr{i}') for i in range(n_other_hunters)])
            # self_play_agents.append([MADQN(f'MADQN{i}') for i in range(n_other_hunters)])
            # self_play_agents.append([SOAleqgAATr(f'SOAleqgAATr{i}') for i in range(n_other_hunters)])
            # self_play_agents.append([SMAlegAATr(f'SMAlegAATr{i}') for i in range(n_other_hunters)])
            self_play_agents.append([RAlegAATr(f'RAlegAATr{i}') for i in range(n_other_hunters)])
            # self_play_agents.append([RDQN(f'RDQN{i}') for i in range(n_other_hunters)])
            # self_play_agents.append([PPO(f'PPO{i}') for i in range(n_other_hunters)])
            self_play_agents.append([QAlegAATr(f'QAlegAATr{i}', enhanced=True) for i in range(n_other_hunters)])
            self_play_agents.append([RawO(f'RawO{i}', enhanced=True) for i in range(n_other_hunters)])
            self_play_agents.append([RAAT(f'RAAT{i}', enhanced=True) for i in range(n_other_hunters)])

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
                sim_label = f'{agent_to_test.name}_{label}_h={height}_w={width}_epoch={epoch_number}'
                run(hunters, height, width, results_file=f'../simulations/adaptability_results/{sim_label}.csv')

    # Coop
    for epoch in range(N_EPOCHS // 2):  # Each epoch generates 2 cooperative results for each agent, so we only want to run half (to avoid sample imbalances)
        print(f'Epoch {epoch + 1}')
        height, width = GRID_SIZE

        cooperators = [Greedy('Greedy1', STAG_NAME), Greedy('Greedy2', STAG_NAME), DQNAgent('DQN1'),
                       AlegAATr('AlegAATr1', lmbda=0.0, ml_model_type='knn', enhanced=True),
                       AleqgAATr('AleqgAATr1'), RAlegAATr('RAlegAATr1'), QAlegAATr('QAlegAATr1', enhanced=True),
                       RawO('RawO1', enhanced=True), RAAT('RAAT1', enhanced=True)]

        agents_to_test = []
        agents_to_test.append(DQNAgent())
        agents_to_test.append(AlegAATr(lmbda=0.0, ml_model_type='knn', enhanced=True))
        agents_to_test.append(AleqgAATr())
        # agents_to_test.append(MADQN())
        # agents_to_test.append(SOAleqgAATr())
        # agents_to_test.append(SMAlegAATr())
        agents_to_test.append(RAlegAATr())
        # agents_to_test.append(RDQN())
        # agents_to_test.append(PPO())
        agents_to_test.append(QAlegAATr(enhanced=True))
        agents_to_test.append(RawO(enhanced=True))
        agents_to_test.append(RAAT(enhanced=True))

        for agent_to_test in agents_to_test:
            hunters = [deepcopy(cooperators[0]), deepcopy(cooperators[1]), deepcopy(agent_to_test)]
            assert len(hunters) == N_HUNTERS
            sim_label = f'{agent_to_test.name}_coop_h={height}_w={width}_epoch={epoch_number}'
            run(hunters, height, width, results_file=f'../simulations/adaptability_results/{sim_label}.csv')

        for agent_to_test in agents_to_test:
            hunters = [deepcopy(cooperators[0])]
            while True:
                idx = np.random.choice(np.arange(2, len(cooperators)))
                new_hunter = cooperators[idx]
                if isinstance(new_hunter, type(agent_to_test)):
                    hunters.append(deepcopy(new_hunter))
                    break
            hunters.append(deepcopy(agent_to_test))
            assert len(hunters) == N_HUNTERS
            sim_label = f'{agent_to_test.name}_coop_h={height}_w={width}_epoch={epoch_number}_twocopies'
            run(hunters, height, width, results_file=f'../simulations/adaptability_results/{sim_label}.csv')


if __name__ == '__main__':
    for foo in range(5):
        adaptability(foo)
