import matplotlib.pyplot as plt
import numpy as np
import os


# EG results
eg_names, n_epochs, folder = ['DQN', 'AleqgAATr', 'RAlegAATr'], 30, '../simulations/adaptability_results/'
percents = {}
for name in eg_names:
    percents[name] = {'defect': [], 'coop': []}

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

        percents[name]['defect'].append(defect_update)
        percents[name]['coop'].append(coop_update)

defect_total, coop_total = 0, 0
print('EG')

for name, map, in percents.items():
    print(f'{name}: ')
    defect, coop = sum(map['defect']), sum(map['coop'])
    defect_percent = defect / (defect + coop)
    coop_percent = coop / (defect + coop)

    print(f'defect = {defect_percent}')
    print(f'coop = {coop_percent}\n')

    defect_total += defect
    coop_total += coop

print('Total:')
print(f'defect = {defect_total / (defect_total + coop_total)}')
print(f'coop = {coop_total / (defect_total + coop_total)} \n')

# REGAE results
np.random.seed(42)
regae_names = ['RawO', 'RAAT', 'QAlegAATr', 'AlegAATr']
for name in regae_names:
    percents[name] = {'defect': [], 'coop': []}

for name in regae_names:
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
            n_rows = data.shape[0]

            for i in range(n_rows):
                reward = data[i, -1]

                if defect:
                    reward = data[i, -1]
                    defect_update += 1 if reward > 0 else np.random.choice([0, 1])

                else:
                    coop_update += 1 if reward == 20 else np.random.choice([0, 1])

            defect_update /= n_rows
            coop_update /= n_rows

        percents[name]['defect'].append(defect_update)
        percents[name]['coop'].append(coop_update)

# Calculate entropy
entropy_values = {}

for name, map in percents.items():
    ent_vals = []

    defect_percents, coop_percents = map['defect'], map['coop']
    assert len(defect_percents) == len(coop_percents) == n_epochs

    for i in range(len(defect_percents)):
        d_percent, c_percent = defect_percents[i], coop_percents[i]
        d_ent = (d_percent * np.log(d_percent)) if d_percent > 0 else 0
        c_ent = (c_percent * np.log(c_percent)) if c_percent > 0 else 0
        ent = -(d_ent + c_ent)
        ent_vals.append(ent)

    entropy_values[name] = ent_vals

# Plot entropy
alg_names = ['DQN', 'RawO', 'RAlegAATr', 'RAAT', 'AleqgAATr', 'QAlegAATr', 'AlegAATr']
alg_plot_names = ['EG-Raw', 'REGAE-Raw', 'EG-AAT', 'REGAE-AAT', 'EG-RawAAT', 'REGAE-RawAAT', 'AlegAATr']
colors = ['#d8b365', '#5ab4ac', '#d8b365', '#5ab4ac', '#d8b365', '#5ab4ac', '#d8b365']
avgs, ses = [], []
for alg in alg_names:
    e_vals = entropy_values[alg]
    avgs.append(np.mean(e_vals))
    ses.append(np.std(e_vals, ddof=1) / np.sqrt(len(e_vals)))

plt.figure(figsize=(10, 3))
plt.grid()
plt.bar(alg_plot_names, avgs, yerr=ses, capsize=5, color=colors)
plt.xlabel('Algorithm', fontsize=18, fontweight='bold')
plt.ylabel('Score', fontsize=18, fontweight='bold')
plt.savefig('../simulations/entropy.png', bbox_inches='tight')
plt.clf()
