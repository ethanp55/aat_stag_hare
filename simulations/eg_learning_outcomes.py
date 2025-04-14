import numpy as np
import os


eg_names, n_epochs, folder = ['DQN', 'AleqgAATr', 'RAlegAATr'], 30, '../simulations/adaptability_results/'
usages = {}
for name in eg_names:
    usages[name] = {'defect': 0, 'coop': 0}

for name in eg_names:
    for epoch in range(n_epochs):
        defect_update, coop_update = 0, 0

        for file in os.listdir(folder):
            if not (name in file and f'epoch={epoch}.csv' in file):
                continue

            # Metadata
            condition = file.split('_')[1]
            defect = condition == 'greedyhare'

            # Data
            data = np.genfromtxt(f'{folder}{file}', delimiter=',', skip_header=0)

            if defect:
                reward_sum = data[:, -1].sum()
                defect_update = 1 if reward_sum > 0 else 0

            else:
                coop_update = 1 if 20 in data[:, -1] else 0

        usages[name]['defect'] += defect_update
        usages[name]['coop'] += coop_update

defect_total, coop_total = 0, 0

for name, map, in usages.items():
    print(f'{name}:')
    defect, coop = map['defect'], map['coop']
    defect_percent = defect / (defect + coop)
    coop_percent = coop / (defect + coop)

    print(f'defect = {defect_percent}')
    print(f'coop = {coop_percent}\n')

    defect_total += defect
    coop_total += coop

print('TOTAL:')
print(f'defect = {defect_total / (defect_total + coop_total)}')
print(f'coop = {coop_total / (defect_total + coop_total)}')
