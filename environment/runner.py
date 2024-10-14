from agents.agent import Agent
import csv
from environment.world import StagHare
import numpy as np
from typing import List, Optional


# TODO:
# - Implement generators
# - Update environment based on feedback
# - Test the environment to make sure it's working properly
# - Implement checkers
# - Implement and train algorithms
# - Run simulations, get results


def run(hunters: List[Agent], height: int = 5, width: int = 5, log: bool = False, results_file: Optional[str] = None,
        generator_file: Optional[str] = None, vector_file: Optional[str] = None) -> None:
    stag_hare = StagHare(height, width, hunters)
    rewards = [0] * len(hunters)

    # Run the environment
    while not stag_hare.is_over():
        round_rewards = stag_hare.transition()

        # Update rewards
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

        # Write any generator usage data and/or vectors
        round_num = stag_hare.state.round_num - 1
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

    # Save data
    if results_file is not None:
        with open(results_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(rewards)
