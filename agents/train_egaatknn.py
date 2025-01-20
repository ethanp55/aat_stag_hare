from aat.train_generators import FavorMoreRecent, GRID_SIZES, N_EPOCHS
from agents.egaatknn import EGAATKNN
from agents.greedy import Greedy
from agents.team_aware import TeamAware
from copy import deepcopy
from environment.runner import run
from utils.utils import HARE_NAME, N_HUNTERS


def train_egaatknn():
    N_EPOCHS = 10
    n_other_hunters = N_HUNTERS - 1

    egaatknn = EGAATKNN(train_knn=True)

    # Run the training process
    for epoch in range(N_EPOCHS):
        print(f'Epoch {epoch + 1}')

        for height, width in GRID_SIZES:
            list_of_other_hunters = []
            list_of_other_hunters.append([TeamAware(f'TeamAware{i}') for i in range(n_other_hunters)])
            list_of_other_hunters.append([Greedy(f'Greedy{i}', HARE_NAME) for i in range(n_other_hunters)])
            list_of_other_hunters.append([FavorMoreRecent(f'FavorMoreRecentTrain{i}') for i in range(n_other_hunters)])

            for other_hunters in list_of_other_hunters:
                assert len(other_hunters) == n_other_hunters
                hunters = deepcopy(other_hunters)
                hunters.append(egaatknn)
                run(hunters, height, width)

                egaatknn.reset()

        egaatknn.train()
        egaatknn.update_epsilon()
        egaatknn.clear_buffer()
