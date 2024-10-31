from agents.alegaatr import AlegAATr
from agents.aleqgaatr import AleqgAATr
from agents.dqn import DQNAgent
from agents.generator import GreedyHareGen, GreedyPlannerHareGen, GreedyPlannerStagGen, TeamAwareGen
from agents.greedy import Greedy
from agents.greedy_prob import GreedyProbabilistic
from agents.madqn import MADQN
from agents.modeller import Modeller
from agents.ppo import PPO
from agents.prob_dest import ProbabilisticDestinations
from agents.qalegaatr import QAlegAATr
from agents.ralegaatr import RAlegAATr
from agents.rawo import RawO
from agents.rdqn import RDQN
from agents.smalegaatr import SMAlegAATr
from agents.soaleqgaatr import SOAleqgAATr
from copy import deepcopy
from environment.runner import run
import os
from utils.utils import N_HUNTERS, STAG_NAME


N_EPOCHS = 5
GRID_SIZES = [(9, 9), (12, 12), (15, 15)]
n_training_iterations = N_EPOCHS * len(GRID_SIZES)
progress_percentage_chunk = int(0.05 * n_training_iterations)
curr_iteration = 0
print(n_training_iterations, progress_percentage_chunk)
n_other_hunters = N_HUNTERS - 1

# names = ['DQN', 'MADQN', 'RDQN', 'AleqgAATr', 'RAlegAATr', 'SOAleqgAATr', 'AlegAATr', 'SMAlegAATr', 'QAlegAATr', 'RawO', 'PPO']
names = ['RawO']

# Reset any existing simulation files (opening a file in write mode will truncate it)
for file in os.listdir('../simulations/results/'):
    name = file.split('_')[0]
    if name in names:
        # if True:
        with open(f'../simulations/results/{file}', 'w', newline='') as _:
            pass

# Run the training process
for epoch in range(N_EPOCHS):
    print(f'Epoch {epoch + 1}')

    for height, width in GRID_SIZES:
        print(height, width)
        if curr_iteration != 0 and progress_percentage_chunk != 0 and curr_iteration % progress_percentage_chunk == 0:
            print(f'{100 * (curr_iteration / n_training_iterations)}%')

        list_of_other_hunters = []
        list_of_other_hunters.append(([GreedyHareGen(f'GreedyHareGen{i}') for i in range(n_other_hunters)], 'greedyhare'))
        list_of_other_hunters.append(([GreedyPlannerHareGen(f'GreedyPlannerHareGen{i}') for i in range(n_other_hunters)], 'greedyplannerhare'))
        list_of_other_hunters.append(([GreedyPlannerStagGen(f'GreedyPlannerStagGen{i}') for i in range(n_other_hunters)], 'greedyplannerstag'))
        list_of_other_hunters.append(([TeamAwareGen(f'TeamAwareGen{i}') for i in range(n_other_hunters)], 'teamawarestag'))
        list_of_other_hunters.append(([Greedy(f'Greedy{i}', STAG_NAME) for i in range(n_other_hunters)], 'greedystag'))
        list_of_other_hunters.append(([Modeller(f'Modeller{i}') for i in range(n_other_hunters)], 'modellerstag'))
        list_of_other_hunters.append(([GreedyProbabilistic(f'GreedyProbabilistic{i}') for i in range(n_other_hunters)], 'greedyprobhare'))
        list_of_other_hunters.append(([ProbabilisticDestinations(f'ProbabilisticDestinations{i}') for i in range(n_other_hunters)], 'probdesthare'))
        list_of_other_hunters.append((None, 'selfplay'))

        for other_hunters, label in list_of_other_hunters:
            agents_to_test = []
            agents_to_test.append(DQNAgent())
            agents_to_test.append(AlegAATr(lmbda=0.0, ml_model_type='knn', enhanced=True))
            agents_to_test.append(AleqgAATr())
            agents_to_test.append(MADQN())
            agents_to_test.append(SOAleqgAATr())
            agents_to_test.append(SMAlegAATr(enhanced=False))
            agents_to_test.append(RAlegAATr())
            agents_to_test.append(RDQN())
            agents_to_test.append(PPO())
            agents_to_test.append(QAlegAATr(enhanced=True))
            agents_to_test.append(RawO(enhanced=True))

            self_play_agents = []
            self_play_agents.append([DQNAgent(f'DQN{i}') for i in range(n_other_hunters)])
            self_play_agents.append([AlegAATr(f'AlegAATr{i}', lmbda=0.0, ml_model_type='knn', enhanced=True) for i in range(n_other_hunters)])
            self_play_agents.append([AleqgAATr(f'AleqgAATr{i}') for i in range(n_other_hunters)])
            self_play_agents.append([MADQN(f'MADQN{i}') for i in range(n_other_hunters)])
            self_play_agents.append([SOAleqgAATr(f'SOAleqgAATr{i}') for i in range(n_other_hunters)])
            self_play_agents.append([SMAlegAATr(f'SMAlegAATr{i}', enhanced=False) for i in range(n_other_hunters)])
            self_play_agents.append([RAlegAATr(f'RAlegAATr{i}') for i in range(n_other_hunters)])
            self_play_agents.append([RDQN(f'RDQN{i}') for i in range(n_other_hunters)])
            self_play_agents.append([PPO(f'PPO{i}') for i in range(n_other_hunters)])
            self_play_agents.append([QAlegAATr(f'QAlegAATr{i}', enhanced=True) for i in range(n_other_hunters)])
            self_play_agents.append([RawO(f'RawO{i}', enhanced=True) for i in range(n_other_hunters)])

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
                run(hunters, height, width, results_file=f'../simulations/results/{sim_label}.csv',
                    generator_file=f'../simulations/generator_usage/{sim_label}.csv',
                    vector_file=f'../simulations/vectors/{sim_label}.csv')

        curr_iteration += 1
