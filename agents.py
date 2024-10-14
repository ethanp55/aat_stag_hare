import numpy as np

from generators import generator_factory

{
    'IsAnyHuntingStag': False,
    'IsAnyHuntingHare': False,
    'IsStagNOpen': True,
    'IsStagSOpen': True,
    'IsStagEOpen': True,
    'IsStagWOpen': True,
    'IsStagClose': 0.45,
    'IsHareClose': 0.2,
    'StagNPathExists': True,
    'StagSPathExists': True,
    'StagEPathExists': True,
    'StagWPathExists': True,
    'HareNPathExists': True,
    'HareSPathExists': True,
    'HareEPathExists': True,
    'HareWPathExists': True
}


class BaseAgent:
    def __init__(self) -> None:
        pass

    def __call__(self, veracity_vec, actions, masked_grid, stag_pos, hare_pos, my_pos, other_poses):
        pass

class StagHunter:
    def __init__(self) -> None:
        self.generators = {
            f'Stag{d}': generator_factory('stag', d)(verbose=False) for d in ['N', 'S', 'E', 'W']
        }

    def __call__(self, veracity_vec, actions, masked_grid, stag_pos, hare_pos, my_pos, other_poses):
        if veracity_vec['IsStagClose'] == 1 / np.sum(masked_grid.shape):
            return 'pass', 'Pass'
        for c in ['StagN', 'StagS', 'StagE', 'StagW']:
            if veracity_vec[f'Is{c}Open'] and veracity_vec[f'{c}PathExists']:
                _, cmds, _ = self.generators[c](masked_grid, my_pos, stag_pos, hare_pos)
                return cmds[0], c
        return 'pass', 'Pass'

class HareHunter:
    def __init__(self) -> None:
        self.generators = {
            f'Hare{d}': generator_factory('hare', d)(verbose=False) for d in ['N', 'S', 'E', 'W']
        }

    def __call__(self, veracity_vec, actions, masked_grid, stag_pos, hare_pos, my_pos, other_poses):
        if veracity_vec['IsHareClose'] == 1 / np.sum(masked_grid.shape):
            return 'pass', 'Pass'
        for c in ['HareN', 'HareS', 'HareE', 'HareW']:
            if veracity_vec[f'Is{c}Open'] and veracity_vec[f'{c}PathExists']:
                _, cmds, _ = self.generators[c](masked_grid, my_pos, stag_pos, hare_pos)
                return cmds[0], c
        return 'pass', 'Pass'

class Opprotunist:
    def __init__(self) -> None:
        self.stag_hunter = StagHunter()
        self.hare_hunter = HareHunter()

    def __call__(self, veracity_vec, actions, masked_grid, stag_pos, hare_pos, my_pos, other_poses):
        if veracity_vec['IsStagClose'] < veracity_vec['IsHareClose']:
            return self.stag_hunter(veracity_vec, actions, masked_grid, stag_pos, hare_pos, my_pos, other_poses)
        else:
            return self.hare_hunter(veracity_vec, actions, masked_grid, stag_pos, hare_pos, my_pos, other_poses)

class Wanderer:
    def __init__(self) -> None:
        pass

    def __call__(self, veracity_vec, actions, masked_grid, stag_pos, hare_pos, my_pos, other_poses):
        print('Random Generator')
        return actions[np.random.choice(len(actions))]