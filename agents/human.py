from agents.agent import Agent
from environment.state import State
from typing import Tuple



from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)


class humanAgent:
    def __init__(self, name) -> None:
        Agent.__init__(self, name)


    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        pass

