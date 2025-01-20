import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

baselines = {'greedyhare': 3.3769999999999993, 'selfplay': 13.760833333333334, 'coop': 13.760833333333334}
results, folder = {}, '../simulations/adaptability_results/'
minimax_val, lowest_reward = 3.3769999999999993, 0

# for file in os.listdir(folder):
#     agent_name = file.split('_')[0]
#     if agent_name not in results:
#         results[agent_name] = {}
#     opp_type = file.split('_')[1]
#     height, width = int(file.split('_')[2].split('=')[1]), int(file.split('_')[3].split('.')[0][2:])
#     comparison = baselines[opp_type]
#     data = np.genfromtxt(f'{folder}{file}', delimiter=',', skip_header=0)[:, 2:]
#
#     if opp_type == 'greedyhare':
#         avg_reward = sum([row[-1] for row in data]) / len(data)
#         regret = (comparison - lowest_reward) - (avg_reward - lowest_reward)
#         val = 1 - max((regret / (comparison - lowest_reward)), 0)
#
#     elif opp_type == 'selfplay':
#         row_avgs = [sum(row) / len(row) for row in data]
#         avg_reward = sum(row_avgs) / len(row_avgs)
#         regret = (comparison - minimax_val) - (avg_reward - minimax_val)
#         val = 1 - min((regret / (comparison - minimax_val)), 1)
#
#     elif opp_type == 'coop':
#         avg_reward = sum([row[-1] for row in data]) / len(data)
#         regret = (comparison - minimax_val) - (avg_reward - minimax_val)
#         val = 1 - min((regret / (comparison - minimax_val)), 1)
#         val = min(val, 1)
#
#     else:
#         raise Exception(f'{opp_type} is not a defined opponent type')
#
#     assert 0 <= val <= 1
#     results[agent_name][opp_type] = val
#
# rc_scores = []
# for agent, res, in results.items():
#     print(agent)
#     defect_score, self_play_score, coop_score = res['greedyhare'], res['selfplay'], res['coop']
#     robust_coop_score = min([defect_score, self_play_score, coop_score])
#     print(f'Defect score: {defect_score}')
#     print(f'Self-play score: {self_play_score}')
#     print(f'Coop score: {coop_score}')
#     print(f'Robust coop score: {robust_coop_score}\n')
#     rc_scores.append((agent, robust_coop_score))
# rc_scores.sort(key=lambda x: x[1], reverse=True)
# print(rc_scores)

N_TRAIN_TEST_RUNS = 30
results_from_every_epoch = {}

for run_num in range(N_TRAIN_TEST_RUNS):
    results = {}
    for file in os.listdir(folder):
        if f'epoch={run_num}' not in file:
            continue
        agent_name = file.split('_')[0]
        if agent_name not in results_from_every_epoch:
            results_from_every_epoch[agent_name] = {}
        if agent_name not in results:
            results[agent_name] = {}
        opp_type = file.split('_')[1]
        height, width = int(file.split('_')[2].split('=')[1]), int(file.split('_')[3].split('.')[0][2:])
        comparison = baselines[opp_type]
        data = np.genfromtxt(f'{folder}{file}', delimiter=',', skip_header=0)
        if len(data.shape) == 1:
            continue
        data = data[:, 2:]

        if opp_type == 'greedyhare':
            avg_reward = sum([row[-1] for row in data]) / len(data)
            regret = (comparison - lowest_reward) - (avg_reward - lowest_reward)
            val = 1 - max((regret / (comparison - lowest_reward)), 0)

        elif opp_type == 'selfplay':
            row_avgs = [sum(row) / len(row) for row in data]
            avg_reward = sum(row_avgs) / len(row_avgs)
            regret = (comparison - minimax_val) - (avg_reward - minimax_val)
            val = 1 - min((regret / (comparison - minimax_val)), 1)

        elif opp_type == 'coop' and 'twocopies' in file:
            row_avgs = [sum(row[1:]) / len(row[1:]) for row in data]
            avg_reward = sum(row_avgs) / len(row_avgs)
            regret = (comparison - minimax_val) - (avg_reward - minimax_val)
            val = 1 - min((regret / (comparison - minimax_val)), 1)

        elif opp_type == 'coop':
            assert 'twocopies' not in file
            avg_reward = sum([row[-1] for row in data]) / len(data)
            regret = (comparison - minimax_val) - (avg_reward - minimax_val)
            val = 1 - min((regret / (comparison - minimax_val)), 1)

        else:
            raise Exception(f'{opp_type} is not a defined opponent type')

        val = max(val, 0)
        val = min(val, 1)
        assert 0 <= val <= 1
        if opp_type == 'coop':
            opp_type_adj = 'coop2' if 'twocopies' in file else 'coop1'
            results[agent_name][opp_type_adj] = val
        else:
            results[agent_name][opp_type] = val

    for agent, res, in results.items():
        defect_score, self_play_score, coop1_score, coop2_score = \
            res['greedyhare'], res['selfplay'], res['coop1'], res['coop2']
        avg_coop_score = (self_play_score + coop1_score + coop2_score) / 3
        adapt_score = min([defect_score, avg_coop_score])
        results_from_every_epoch[agent]['d'] = results_from_every_epoch[agent].get('d', []) + [defect_score]
        results_from_every_epoch[agent]['c'] = results_from_every_epoch[agent].get('c', []) + [avg_coop_score]
        results_from_every_epoch[agent]['a'] = results_from_every_epoch[agent].get('a', []) + [adapt_score]


alg_names = ['DQN', 'RAlegAATr', 'AleqgAATr', 'RawO', 'RAAT', 'QAlegAATr', 'AlegAATr']
alg_plot_names = ['EG-Raw', 'EG-AAT', 'EG-RawAAT', 'REGAE-Raw', 'REGAE-AAT', 'REGAE-RawAAT', 'AlegAATr']
for cond in ['d', 'c', 'a']:
    avgs, ses = [], []
    for alg in alg_names:
        alg_data = results_from_every_epoch[alg][cond]
        avgs.append(np.mean(alg_data))
        ses.append(np.std(alg_data, ddof=1) / np.sqrt(len(alg_data)))

    plt.figure(figsize=(10, 3))
    plt.grid()
    plt.bar(alg_plot_names, avgs, yerr=ses, capsize=5)
    plt.xlabel('Algorithm', fontsize=18, fontweight='bold')
    plt.ylabel('Score', fontsize=18, fontweight='bold')
    plt.savefig(f'../simulations/{cond}.png', bbox_inches='tight')
    plt.clf()

