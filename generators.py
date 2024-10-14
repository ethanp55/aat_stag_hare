import numpy as np

from astar import a_star_search

def gen_probabilities(results, alpha=1.0, beta=1.0, w_alpha=2.0, w_beta=2.0):
    n_success = np.sum(results)
    n_failures = len(results) - n_success
    return (alpha + w_alpha * n_success) / (alpha + w_alpha * n_success + beta + w_beta * n_failures)


def generator_factory(target, goal_direction):

    class Generator:
        def __init__(self, verbose=False) -> None:
            self.target = target
            self.goal_direction = goal_direction
            directions = {
                'E': (0, 1), 
                'W': (0, -1), 
                'N': (1, 0), 
                'S': (-1, 0)
            }

            self.delta2cmd = {
                0: {
                    -1: 'down',
                    1: 'up'
                },
                1: { 
                    0: 'right'
                },
                -1: {
                    0: 'left'
                }
            }

            self.verbose = verbose

            assert goal_direction in directions.keys()
            self.goal_offset = directions[goal_direction]

            self.name = f'move2{self.target}{self.goal_direction}'

        def __call__(self, grid, start_position, stag_position, hare_position):
            if self.verbose:
                print(f'Call: {self.name}')
            active_target = stag_position if self.target == 'stag' else hare_position
            dx, dy = self.goal_offset
            end = (active_target[0] + dx, active_target[1] + dy)
            if grid[end] != 1:
                #print('Skip')
                return [], [], False
            
            res = a_star_search(grid, start_position, end)
            if res is not None:
                solved_grid = np.zeros_like(grid)
                solved_grid[end] = -1
                solved_grid[start_position] = -2
                for p in res:
                    solved_grid[p] = 1
                #print('Path found')
                return res, [self.delta2cmd[c[1]][c[0]] for c in np.diff(res, axis=0)], True
            
            #print('No path')
            return [], [], False

        def prob(self, agent_id, grids, positions, stag_positions, hare_positions):
            alpha = 1.0
            beta = 1.0
            w_alpha = 2.0
            w_beta = 2.0
            
            results = []

            for i, (pos, grid, stag_pos, hare_pos) in enumerate(zip(positions, grids, stag_positions, hare_positions)):
                if i == len(positions) - 1:
                    break
                path, cmds, success = self(np.logical_or(grid == 0, grid == (agent_id+1)).astype(int), pos[agent_id], stag_pos, hare_pos)
                expected_pos = pos[agent_id]
                action = None
                if success:
                    expected_pos = path[1]
                    action = cmds[0]
                #print(f'{action}: {pos[agent_id]} -> {expected_pos} =?= {positions[i+1][agent_id]}')
                dist = np.linalg.norm(expected_pos - np.asarray(positions[i+1][agent_id]), ord=1)
                penalty = dist #1 - np.exp(dist)
                #print(f'p({self.name}): {penalty}')
                if penalty == 0:
                    results.append(1)
                else:
                    results.append(0)

            return gen_probabilities(results, alpha, beta, w_alpha, w_beta), results

    return Generator
