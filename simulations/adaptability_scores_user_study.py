import json
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

baselines = {'greedyhare': 3.3769999999999993, 'selfplay': 13.760833333333334, 'coop': 13.760833333333334}
results, folder = {}, '../simulations/adaptability_results/'
minimax_val, lowest_reward = 3.3769999999999993, 0
with open('./user_study_data/stag_hare_top_level_3.json', 'r') as file:
    user_study_results = json.load(file)

scenario_mapping = {
    'A': 'greedyhare',
    'B': 'selfplay',
    'C': 'coop2',
    'D': 'coop1'
}
scores, sp_rounds, coop2_rounds = {}, set(), set()

for name, results in user_study_results.items():
    for round, round_results in results.items():
        scenario, reward = round_results['situation'], round_results['new_points']
        s_mapping = scenario_mapping[scenario]
        comparison = baselines[s_mapping] if 'coop' not in s_mapping else baselines['coop']

        if s_mapping == 'greedyhare':
            regret = (comparison - lowest_reward) - (reward - lowest_reward)
            val = 1 - max((regret / (comparison - lowest_reward)), 0)

        elif s_mapping == 'coop1':
            regret = (comparison - minimax_val) - (reward - minimax_val)
            val = 1 - min((regret / (comparison - minimax_val)), 1)

        elif s_mapping == 'coop2':
            if round in coop2_rounds:
                continue
            coop2_rounds.add(round)

            other_reward = None
            for other_name, other_results in user_study_results.items():
                if other_name == name:
                    continue
                for other_round, other_round_results in other_results.items():
                    if other_round == round and other_round_results['situation'] == scenario:
                        other_reward = other_round_results['new_points']
                        break
                if other_reward is not None:
                    break

            assert other_reward is not None
            avg_reward = (reward + other_reward) / 2
            regret = (comparison - minimax_val) - (avg_reward - minimax_val)
            val = 1 - min((regret / (comparison - minimax_val)), 1)

        elif s_mapping == 'selfplay':
            if round in sp_rounds:
                continue
            sp_rounds.add(round)

            other_rewards = []
            for other_name, other_results in user_study_results.items():
                if other_name == name:
                    continue
                for other_round, other_round_results in other_results.items():
                    if other_round == round and other_round_results['situation'] == scenario:
                        other_rewards.append(other_round_results['new_points'])
                        break
                if len(other_rewards) == 2:
                    break

            assert len(other_rewards) == 2
            avg_reward = (reward + sum(other_rewards)) / 3
            regret = (comparison - minimax_val) - (avg_reward - minimax_val)
            val = 1 - min((regret / (comparison - minimax_val)), 1)

        else:
            raise Exception(f'{s_mapping} is not a defined scenario')

        val = max(val, 0)
        val = min(val, 1)
        assert 0 <= val <= 1
        scores[s_mapping] = scores.get(s_mapping, []) + [val]

defect_scores, self_play_scores, coop1_scores, coop2_scores = \
    scores['greedyhare'], scores['selfplay'], scores['coop1'], scores['coop2']
coop_scores = [(self_play_scores[i] + coop1_scores[i] + coop2_scores[i]) / 3 for i in range(len(self_play_scores))]
adaptability_scores = [min(defect_scores[i], coop_scores[i]) for i in range(len(defect_scores))]

colors = ['#edf8b1', '#7fcdbb', '#2c7fb8']
avgs, ses = [], []
for scores in [defect_scores, coop_scores, adaptability_scores]:
    avgs.append(np.mean(scores))
    ses.append(np.std(scores, ddof=1) / np.sqrt(len(scores)))

    print(avgs[-1])

plt.figure(figsize=(10, 3))
plt.grid()
plt.bar(['Defect', 'Coop.', 'Adapt.'], avgs, yerr=ses, capsize=5, color=colors)
plt.xlabel('Score Type', fontsize=18, fontweight='bold')
plt.ylabel('Score', fontsize=18, fontweight='bold')
plt.savefig(f'../simulations/user_study.png', bbox_inches='tight')
plt.clf()


# N_TRAIN_TEST_RUNS = 30
# results_from_every_epoch = {}
#
# for run_num in range(N_TRAIN_TEST_RUNS):
#     results = {}
#     for file in os.listdir(folder):
#         if f'epoch={run_num}' not in file:
#             continue
#         agent_name = file.split('_')[0]
#         if agent_name not in results_from_every_epoch:
#             results_from_every_epoch[agent_name] = {}
#         if agent_name not in results:
#             results[agent_name] = {}
#         opp_type = file.split('_')[1]
#         height, width = int(file.split('_')[2].split('=')[1]), int(file.split('_')[3].split('.')[0][2:])
#         comparison = baselines[opp_type]
#         data = np.genfromtxt(f'{folder}{file}', delimiter=',', skip_header=0)
#         if len(data.shape) == 1:
#             continue
#         data = data[:, 2:]
#
#         if opp_type == 'greedyhare':
#             avg_reward = sum([row[-1] for row in data]) / len(data)
#             regret = (comparison - lowest_reward) - (avg_reward - lowest_reward)
#             val = 1 - max((regret / (comparison - lowest_reward)), 0)
#
#         elif opp_type == 'selfplay':
#             row_avgs = [sum(row) / len(row) for row in data]
#             avg_reward = sum(row_avgs) / len(row_avgs)
#             regret = (comparison - minimax_val) - (avg_reward - minimax_val)
#             val = 1 - min((regret / (comparison - minimax_val)), 1)
#
#         elif opp_type == 'coop' and 'twocopies' in file:
#             row_avgs = [sum(row[1:]) / len(row[1:]) for row in data]
#             avg_reward = sum(row_avgs) / len(row_avgs)
#             regret = (comparison - minimax_val) - (avg_reward - minimax_val)
#             val = 1 - min((regret / (comparison - minimax_val)), 1)
#
#         elif opp_type == 'coop':
#             assert 'twocopies' not in file
#             avg_reward = sum([row[-1] for row in data]) / len(data)
#             regret = (comparison - minimax_val) - (avg_reward - minimax_val)
#             val = 1 - min((regret / (comparison - minimax_val)), 1)
#
#         else:
#             raise Exception(f'{opp_type} is not a defined opponent type')
#
#         val = max(val, 0)
#         val = min(val, 1)
#         assert 0 <= val <= 1
#         if opp_type == 'coop':
#             opp_type_adj = 'coop2' if 'twocopies' in file else 'coop1'
#             results[agent_name][opp_type_adj] = val
#         else:
#             results[agent_name][opp_type] = val
#
#     for agent, res, in results.items():
#         defect_score, self_play_score, coop1_score, coop2_score = \
#             res['greedyhare'], res['selfplay'], res['coop1'], res['coop2']
#         avg_coop_score = (self_play_score + coop1_score + coop2_score) / 3
#         adapt_score = min([defect_score, avg_coop_score])
#         results_from_every_epoch[agent]['d'] = results_from_every_epoch[agent].get('d', []) + [defect_score]
#         results_from_every_epoch[agent]['c'] = results_from_every_epoch[agent].get('c', []) + [avg_coop_score]
#         results_from_every_epoch[agent]['a'] = results_from_every_epoch[agent].get('a', []) + [adapt_score]
#
#
# alg_names = ['DQN', 'RawO', 'RAlegAATr', 'RAAT', 'AleqgAATr', 'QAlegAATr', 'AlegAATr']
# alg_plot_names = ['EG-Raw', 'REGAE-Raw', 'EG-AAT', 'REGAE-AAT', 'EG-RawAAT', 'REGAE-RawAAT', 'AlegAATr']
# colors = ['#ef8a62', '#67a9cf', '#ef8a62', '#67a9cf', '#ef8a62', '#67a9cf', '#999999']
# scores, score_types, learning_algs, features, domain = [], [], [], [], []
# for cond in ['d', 'c', 'a']:
#     avgs, ses = [], []
#     for alg in alg_names:
#         alg_data = results_from_every_epoch[alg][cond]
#         avgs.append(np.mean(alg_data))
#         ses.append(np.std(alg_data, ddof=1) / np.sqrt(len(alg_data)))
#
#         n_samples = len(alg_data)
#         scores.extend(alg_data)
#         score_types.extend([cond] * n_samples)
#         name = alg_plot_names[alg_names.index(alg)]
#         learning_alg = name.split('-')[0] if alg != 'AlegAATr' else 'REGAEKNN'
#         feature_set = name.split('-')[1] if alg != 'AlegAATr' else 'AATKNN'
#         learning_algs.extend([learning_alg] * n_samples)
#         features.extend([feature_set] * n_samples)
#         domain.extend(['pursuit'] * n_samples)
#
#     plt.figure(figsize=(10, 3))
#     plt.grid()
#     plt.bar(alg_plot_names, avgs, yerr=ses, capsize=5, color=colors)
#     plt.xlabel('Algorithm', fontsize=18, fontweight='bold')
#     plt.ylabel('Score', fontsize=18, fontweight='bold')
#     plt.savefig(f'../simulations/{cond}.png', bbox_inches='tight')
#     plt.clf()
#
# df = pd.DataFrame({
#     'score': scores,
#     'score_type': score_types,
#     'learning_alg': learning_algs,
#     'feature_set': features,
#     'domain': domain
# })
# df.to_csv('./pursuit_adaptability_results.csv', index=False)
