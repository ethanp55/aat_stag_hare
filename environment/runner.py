from agents.agent import Agent
import csv
from environment.world import StagHare
import numpy as np
from typing import List, Optional


# TODO:
# - Implement generators
#   - Team aware (stag) - seems better in small grids - DONE
#   - Greedy planner (stag) - seems better in medium/large grids - DONE
#   - Greedy (hare) - seems better in small grids - DONE
#   - Greedy planner (hare) - seems better in medium/large grids - DONE
# - Implement other agents for testing
#   - Generators (no need to do anything once they're done in the previous step) - DONE
#   - Greedy (stag) - DONE
#   - Modeller (stag) - DONE
#   - Greedy prob (hare) - DONE
#   - Prob dest (hare) - DONE
# - Implement checkers
# - Implement and train algorithms
# - Run simulations, get results


def run(hunters: List[Agent], height: int = 5, width: int = 5, log: bool = False, results_file: Optional[str] = None,
        generator_file: Optional[str] = None, vector_file: Optional[str] = None) -> None:
    # Sometimes the environment can be randomly initialized so that hunters are immediately placed in a surrounding
    # position
    while True:
        stag_hare = StagHare(height, width, hunters)
        if not stag_hare.is_over():
            break
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
