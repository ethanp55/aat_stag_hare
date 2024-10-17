from agents.agent import Agent
import csv
from environment.world import StagHare
import numpy as np
from typing import List, Optional


def run(hunters: List[Agent], height: int = 10, width: int = 10, log: bool = False, results_file: Optional[str] = None,
        generator_file: Optional[str] = None, vector_file: Optional[str] = None) -> List[float]:
    # Reset any generator usage data and/or vector data
    if generator_file is not None:
        with open(generator_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['round', 'generator'])
    if vector_file is not None:
        with open(vector_file, 'w', newline='') as _:
            pass

    # Sometimes the environment can be randomly initialized so that hunters are immediately placed in a surrounding
    # position
    while True:
        stag_hare = StagHare(height, width, hunters)
        if not stag_hare.is_over():
            break
    rewards = [0] * (len(hunters) + 2)

    # Run the environment
    while not stag_hare.is_over():
        round_num = stag_hare.state.round_num
        round_rewards = stag_hare.transition()

        # Update rewards
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        # Write any generator usage data and/or vectors
        if generator_file is not None:
            with open(generator_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([round_num, hunters[-1].generator_to_use_idx])
        if vector_file is not None:
            with open(vector_file, 'a', newline='') as file:
                writer = csv.writer(file)
                row = np.concatenate([np.array([hunters[-1].generator_to_use_idx]), hunters[-1].tracked_vector])
                writer.writerow(np.squeeze(row))

        if log:
            print(f'State:\n{stag_hare.state}')
            print(f'Rewards: {round_rewards}\n')

    # Some agents need to store the final results
    stag_hare.transition()

    # Save data
    if results_file is not None:
        with open(results_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(rewards)

    return rewards
