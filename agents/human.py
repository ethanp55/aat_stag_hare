from agents.agent import Agent
from environment.state import State
from typing import Tuple




class humanAgent:
    def __init__(self, name) -> None:
        Agent.__init__(self, name)


    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:

        # so this is going to need to change, becuase we want the actions to be toggleable by the player
        # this is going to need to take in input from the other dudes, which is unfortuante.
        return 1,1 # this is NOT final. just need to make a gui first.