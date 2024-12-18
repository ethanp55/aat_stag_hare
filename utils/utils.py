HARE_NAME = 'hare'
STAG_NAME = 'stag'
AVAILABLE = -1  # A cell in the grid with this value means it is available/not taken
VERTICAL, HORIZONTAL = 'vertical', 'horizontal'
POSSIBLE_MOVEMENTS = [VERTICAL, HORIZONTAL]  # Up/down, left/right
POSSIBLE_DELTA_VALS = [-1, 0, 1]  # Left/down, stay, right/up
MAX_MOVEMENT_UNITS = 1
LEFT, RIGHT, UP, DOWN, NONE = 0, 1, 2, 3, 4
HARE_REWARD = 10
STAG_REWARD = 60
N_REQUIRED_TO_CAPTURE_HARE = 1
N_REQUIRED_TO_CAPTURE_STAG = 3
N_HUNTERS = 3
