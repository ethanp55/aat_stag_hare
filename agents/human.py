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

    def set_player_position(self, pressed_keys, state):
        curr_row, curr_col = state.agent_positions[self.name]
        if pressed_keys[K_UP]:
            curr_row += 1
        if pressed_keys[K_DOWN]:
            curr_row -= 1
        if pressed_keys[K_LEFT]:
            curr_col -= 1
        if pressed_keys[K_RIGHT]:
            curr_col += 1

        return curr_row, curr_col
    #state.agent_positions[self.name] = (curr_row, curr_col) # updates the actual position

    def get_player_position(self, state):
        curr_row, curr_col = state.agent_positions[self.name]
        return curr_row, curr_col

