import numpy as np
from generators import generator_factory

#TODO: add checkers for trust for all agents/num trusted agents

# Meta Features
def pos_dist(targ_pos, agent_pos):
    return np.linalg.norm(np.asarray(targ_pos) - np.asarray(agent_pos), ord=1)

def is_open(grid, pos):
    return grid[pos] == 0

def is_hunting(probs_dict, threshold, targ):
    return probs_dict[targ] > threshold

def is_going(probs_dict, threshold, targ, dir):
    return probs_dict[f'move2{targ}{dir}'] > threshold

# Features
def any_hunting_factory(target):
    class HuntingChecker:
        def __init__(self) -> None:
            self.target = target
        
        def __call__(self, prob_dicts, threshold=0.738):
            for probs in prob_dicts:
                if is_hunting(probs, threshold, self.target):
                    return True
            return False
        
    return HuntingChecker

def is_open_factory(direction, target):
    class IsOpenChecker:
        def __init__(self) -> None:
            self.target = target
            self.direction = direction
            self._directions_map = {
                'E': (0, 1), 
                'W': (0, -1), 
                'N': (1, 0), 
                'S': (-1, 0),
                'P': (0, 0)
            }

        def __call__(self, grid, stag_position, hare_position):
            position = stag_position if self.target == 'stag' else hare_position
            dx, dy = self._directions_map[self.direction]
            end = (position[0] + dx, position[1] + dy)
            return is_open(grid, end)
    
    return IsOpenChecker

def path_exists_factory(target, direction):
    class PathExistsChecker:
        def __init__(self) -> None:
            self.generator =  generator_factory(target, direction)()

        def __call__(self, grid, start_position, stag_position, hare_position):
            _, _, success = self.generator(grid, start_position, stag_position, hare_position)
            return success
    
    return PathExistsChecker


def is_close_factory(target):
    class IsCloseChecker:
        def __init__(self) -> None:
            self.target = target

        def __call__(self, current_position, stag_position, hare_position):
            if self.target == 'stag':
                return pos_dist(current_position, stag_position)
            elif self.target == 'hare':
                return pos_dist(current_position, hare_position)
            return 0.

    return IsCloseChecker

# Checker Generator
class CheckerGenerator:
    def __init__(self) -> None:
        self.hunting_checkers = {
            'IsAnyHuntingStag': any_hunting_factory('stag')(),
            'IsAnyHuntingHare': any_hunting_factory('hare')()
        }

        self.open_checkers = {
            f'Is{t.title()}{d}Open': is_open_factory(d, t)() for t in ['stag', 'hare'] for d in ['N', 'S', 'E', 'W']
        }

        self.close_checkers = {
            f'Is{t.title()}Close': is_close_factory(t)() for t in ['stag', 'hare']
        }

        self.path_exists = {
            f'{t.title()}{d}PathExists': path_exists_factory(t, d)() for t in ['stag', 'hare'] for d in ['N', 'S', 'E', 'W']
        }

    def get_veracity(self, grid_world, agent_id):
        prob_dicts = grid_world.get_gen_probs()

        return {
            **{
                k: v(prob_dicts) 
                    for k, v in self.hunting_checkers.items()
            },
            **{
                k: v(grid_world.grid, grid_world.stag_position, grid_world.hare_position) 
                    for k, v in self.open_checkers.items()
            },
            **{
                k: v(grid_world.agent_positions[agent_id], grid_world.stag_position, grid_world.hare_position) / np.sum(grid_world.grid.shape) 
                    for k, v in self.close_checkers.items()
            },
            **{
                k: v(np.logical_or(grid_world.grid == 0, grid_world.grid == (agent_id+1)).astype(int), grid_world.agent_positions[agent_id], grid_world.stag_position, grid_world.hare_position)
                    for k, v in self.path_exists.items()
            }
        }