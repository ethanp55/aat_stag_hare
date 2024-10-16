import numpy as np
import pandas as pd
import os
from statsmodels.stats.multicomp import pairwise_tukeyhsd

folder = '../simulations/results/'
names, grid_dims,  opponent_types = [], [], []
final_rewards, final_reward_sums = [], []

for file in os.listdir(folder):
    agent_name = file.split('_')[0]
    height = file.split('h=')[1].split('_')[0]
    width = file.split('w=')[1].split('.')[0]
    opp_type = file[len(agent_name) + 1:].split('_')[0]
    data = np.genfromtxt(f'{folder}{file}', delimiter=',', skip_header=0)
    if data.shape[0] == 0:
        continue
    if len(data.shape) == 1:
        data = data.reshape(1, -1)

    for row in data:
        # Add the condition info
        names.append(agent_name)
        grid_dims.append(f'{height}_{width}')
        opponent_types.append(opp_type)

        # Calculate and add the results
        agent_reward = row[-1]
        final_rewards.append(agent_reward)
        final_reward_sums.append(sum(row))

# Store in a csv file for analysis in Google Sheets (or MS Excel)
df = pd.DataFrame(
    {
        'algorithm': names,
        'grid_dims': grid_dims,
        'opponent_type': opponent_types,
        'reward_sum': final_reward_sums,
        'agent_final_reward': final_rewards,
    }
)
df.to_csv('../simulations/formatted_results_hand_picked_stag_hare.csv', index=False)


# Effect sizes for final popularities (overall)
def _cohens_d(group1, group2):
    mean_diff = np.mean(group1) - np.mean(group2)
    pooled_std = np.sqrt((np.std(group1, ddof=1) ** 2 + np.std(group2, ddof=1) ** 2) / 2)

    return mean_diff / pooled_std


alegaatr_final_rewards, latex_df = df[df['algorithm'] == 'AlegAATr']['agent_final_reward'], []

for name in df['algorithm'].unique():
    if name == 'AlegAATr':
        continue
    other_final_rewards = df[df['algorithm'] == name]['agent_final_reward']
    d = _cohens_d(alegaatr_final_rewards, other_final_rewards)

    # print(f'Cohen\'s d AlegAATr vs. {name}: {d}')
    latex_df.append((f'AlegAATr vs. {name}', round(d, 3)))

latex_df = pd.DataFrame(latex_df, columns=['Comparison', 'Effect Size'])
# print(latex_df.to_latex(index=False))
print(latex_df)

print('\nFINAL REWARDS:')
print(pairwise_tukeyhsd(endog=df['agent_final_reward'], groups=df['algorithm'], alpha=0.05))

print('\nFINAL REWARD SUMS:')
print(pairwise_tukeyhsd(endog=df['reward_sum'], groups=df['algorithm'], alpha=0.05))
