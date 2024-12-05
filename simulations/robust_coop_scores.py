import numpy as np
import os
from scipy.stats import hmean

baselines = {'greedyhare': 3.431833333333333, 'selfplay': 13.66933333333333}
results, folder = {}, '../simulations/results/'
HEIGHT, WIDTH = 15, 15

for file in os.listdir(folder):
    agent_name = file.split('_')[0]
    if agent_name not in results:
        results[agent_name] = {}
    opp_type = file.split('_')[1]
    height, width = int(file.split('_')[2].split('=')[1]), int(file.split('_')[3].split('.')[0][2:])
    if opp_type not in baselines or height != HEIGHT or width != WIDTH:
        continue
    comparison = baselines[opp_type]
    data = np.genfromtxt(f'{folder}{file}', delimiter=',', skip_header=0)

    if opp_type == 'greedyhare':
        avg_final_reward = sum([row[-1] for row in data]) / len(data)
        val = min(avg_final_reward, comparison) / comparison

    elif opp_type == 'selfplay':
        all_deviations = []
        for row in data[:, 2:]:
            deviations = [1 - ((comparison - min(reward, comparison)) / comparison) for reward in row]
            all_deviations.append(sum(deviations) / len(deviations))
        val = sum(all_deviations) / len(all_deviations)
        # avgs = [sum(row) / len(row) for row in data[:, 2:]]
        # val = min((sum(avgs) / len(avgs)), comparison) / comparison

    else:
        raise Exception(f'{opp_type} is not a defined opponent type')

    assert 0 <= val <= 1
    # results[agent_name][opp_type] = results[agent_name].get(opp_type, []) + [val]
    results[agent_name][opp_type] = val

rc_scores = []
for agent, res, in results.items():
    print(agent)
    # defect_scores, coop_scores = res['bullypunish'], res['cooppunish']
    # defect_score = sum(defect_scores) / len(defect_scores)
    # coop_score = hmean(coop_scores)
    defect_score, coop_score = res['greedyhare'], res['selfplay']
    robust_coop_score = min(defect_score, coop_score)
    print(f'Defect score: {defect_score}')
    print(f'Coop score: {coop_score}')
    print(f'Robust coop score: {robust_coop_score}\n')
    rc_scores.append((agent, robust_coop_score))
rc_scores.sort(key=lambda x: x[1], reverse=True)
print(rc_scores)
