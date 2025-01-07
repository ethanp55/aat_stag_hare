from environment.runner import run
from agents.greedy import Greedy
from utils.utils import HARE_NAME, STAG_NAME


total_rewards = []

for _ in range(10000):
    hunters = [Greedy(f'G{i}', HARE_NAME) for i in range(3)]
    rewards = run(hunters, 15, 15)
    total_rewards.append(rewards[-1])

print(sum(total_rewards) / len(total_rewards))
