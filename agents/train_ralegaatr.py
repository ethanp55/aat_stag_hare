from aat.train_generators import FavorMoreRecent, GRID_SIZES, N_EPOCHS
from agents.greedy import Greedy
from agents.ralegaatr import RAlegAATr
from agents.team_aware import TeamAware
from copy import deepcopy
from environment.runner import run
from utils.utils import HARE_NAME, N_HUNTERS


n_training_iterations = N_EPOCHS * len(GRID_SIZES)
progress_percentage_chunk = int(0.05 * n_training_iterations)
curr_iteration = 0
print(n_training_iterations, progress_percentage_chunk)
n_other_hunters = N_HUNTERS - 1

ralegaatr = RAlegAATr(train_network=True)

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
            hunters = deepcopy(other_hunters)
            hunters.append(ralegaatr)
            run(hunters, height, width)

            ralegaatr.reset()

        curr_iteration += 1

    ralegaatr.train()
    ralegaatr.update_epsilon()
    ralegaatr.update_networks()
    ralegaatr.clear_buffer()
