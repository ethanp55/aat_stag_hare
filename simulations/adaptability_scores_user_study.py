import json
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

baselines = {'greedyhare': 3.3769999999999993, 'selfplay': 20, 'coop': 20}
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

# Time plot
plt.figure(figsize=(10, 3))
plt.grid()
labels = ['Defect', 'Coop.', 'Adapt.']
for i, score_vals in enumerate([defect_scores, coop_scores, adaptability_scores]):
    plt.plot(score_vals, color=colors[i], label=labels[i])
plt.xlabel('Score Type', fontsize=18, fontweight='bold')
plt.ylabel('Score', fontsize=18, fontweight='bold')
plt.legend(loc='best')
plt.savefig(f'../simulations/user_study_time.png', bbox_inches='tight')
plt.clf()


# Bar plot
avgs, ses = [], []
for scores in [defect_scores, coop_scores, adaptability_scores]:
    avgs.append(np.mean(scores))
    ses.append(np.std(scores, ddof=1) / np.sqrt(len(scores)))

    print(avgs[-1])

plt.figure(figsize=(10, 3))
plt.grid()
plt.bar(labels, avgs, yerr=ses, capsize=5, color=colors)
plt.xlabel('Score Type', fontsize=18, fontweight='bold')
plt.ylabel('Score', fontsize=18, fontweight='bold')
plt.savefig(f'../simulations/user_study.png', bbox_inches='tight')
plt.clf()
