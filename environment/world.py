from agents.agent import Agent
from agents.prey import Prey
from environment.state import State
import numpy as np
from typing import List
from utils.utils import HARE_NAME, N_HUNTERS, STAG_NAME


class StagHare:
    def __init__(self, height: int, width: int, hunters: List[Agent]) -> None:
        # Make sure we can set the grid up properly
        n_hunters = len(hunters)

        if n_hunters != N_HUNTERS:
            raise Exception(f'There have to be {N_HUNTERS} hunters')

        if height * width < n_hunters + 2:
            raise Exception(f'Not enough cells in the grid for the hare, stag, and {n_hunters} hunters')

        # Generate a list of agents (the hunters, hare, and stage)
        self.agents = [Prey(HARE_NAME), Prey(STAG_NAME)] + hunters

        # Initialize the state and rewards
        self.agent_names = [agent.name for agent in self.agents]
        self.state = State(height, width, self.agent_names)
        self.rewards = [0] * len(self.agent_names)

    def transition(self) -> List[float]:
        # Randomize the order in which the agents will act
        indices = list(range(len(self.agents)))
        np.random.shuffle(indices)
        action_map = {}
        round_num = self.state.round_num

        for i in indices:
            agent = self.agents[i]
            reward = 0 if (i == 0 or i == 1) else self.rewards[i]
            new_row, new_col = agent.act(self.state, reward, round_num)
            print(self.agent_names[i], reward)
            action_map[agent.name] = (new_row, new_col)

        self.rewards = self.state.process_actions(action_map)

        return self.rewards

    def is_over(self) -> bool:
        # As soon as one of the prey agents is captured, we're done
        return self.state.hare_captured() or self.state.stag_captured()
