from agents.agent import Agent
from agents.prey import Prey
from environment.state import State
import numpy as np
from typing import List
from utils.utils import HARE_NAME, N_MIN_HUNTERS, STAG_NAME


class StagHare:
    def __init__(self, height: int, width: int, hunters: List[Agent]) -> None:
        # Make sure we can set the grid up properly
        n_hunters = len(hunters)

        if n_hunters < N_MIN_HUNTERS:
            raise Exception(f'There have to be at least {N_MIN_HUNTERS} hunters')

        if height * width < n_hunters + 2:
            raise Exception(f'Not enough cells in the grid for the hare, stag, and {n_hunters} hunters')

        # Generate a list of agents (the hunters, hare, and stage)
        self.agents = [Prey(HARE_NAME), Prey(STAG_NAME)] + hunters

        # Initialize the state
        agent_names = [agent.name for agent in self.agents]
        self.state = State(height, width, agent_names)

    def transition(self) -> List[float]:
        # Randomize the order in which the agents will act
        indices = list(range(len(self.agents)))
        np.random.shuffle(indices)
        action_map = {}

        for i in indices:
            agent = self.agents[i]
            new_row, new_col = agent.act(self.state)
            action_map[agent.name] = (new_row, new_col)

        return self.state.process_actions(action_map)

    def is_over(self) -> bool:
        # As soon as one of the prey agents is captured, we're done
        return self.state.hare_captured() or self.state.stag_captured()
