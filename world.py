import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import random

from maxqueue import MaxSizeQueue
from generators import generator_factory, gen_probabilities
from checkers import CheckerGenerator
from agents import StagHunter, HareHunter, Opprotunist, Wanderer

class GridWorld:
    entity2value = {
        'stag': 255,
        'hare': 256,
        'wall': -1
    }

    def __init__(self, width, height, num_agents=1, headless=False):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)  # Initialize grid with zeros
        self.grid[:, 0] = GridWorld.entity2value['wall']
        self.grid[:, -1] = GridWorld.entity2value['wall']
        self.grid[-1] = GridWorld.entity2value['wall']
        self.grid[0] = GridWorld.entity2value['wall']

        open_spaces = np.argwhere(self.grid == 0)
        player_positions = [(p[0], p[1]) for p in open_spaces[np.random.choice(len(open_spaces), num_agents + 2, replace=False)]]
        self.agent_positions = player_positions[:num_agents]
        self.stag_position = player_positions[-1]
        self.hare_position = player_positions[-2]
        self.grid[self.stag_position] = GridWorld.entity2value['stag']
        self.grid[self.hare_position] = GridWorld.entity2value['hare']
        for i, position in enumerate(self.agent_positions):
            self.grid[position] = i+1  # Mark agent's position on the grid as occupied

        self.generators = [
            generator_factory(t, d)() for t in ['stag', 'hare'] for d in ['N', 'S', 'E', 'W']
        ]

        print('Generators')
        for g in self.generators:
            print(g.name)

        self.actors = [
            Opprotunist() for i in range(num_agents)
        ]

        self.active_agent = 0
        self.step = 0

        self.history_window = 10
        self.reset_history()

        self.checker_gen = CheckerGenerator()

        self.headless = headless
        if not self.headless:
            self.fig, self.ax = plt.subplots(1, 3, figsize=(self.grid.shape[1]/2 * 3, self.grid.shape[0]/2))
            self.display_grid()
            self.cid = self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
            plt.show()

    def add_history(self):
        self.grid_history.enqueue(deepcopy(self.grid))
        self.agent_history.enqueue(deepcopy(self.agent_positions))
        self.hare_history.enqueue(deepcopy(self.hare_position))
        self.stag_history.enqueue(deepcopy(self.stag_position))

    def reset_history(self):
        self.grid_history = MaxSizeQueue(self.history_window)
        self.agent_history = MaxSizeQueue(self.history_window)
        self.hare_history = MaxSizeQueue(self.history_window)
        self.stag_history = MaxSizeQueue(self.history_window)

    def move_agent(self, action, agent_id):
        if agent_id >= len(self.agent_positions) or agent_id < 0:
            return False
        y, x = self.agent_positions[agent_id]
        if action == "up":
            new_x, new_y = x, y + 1
        elif action == "down":
            new_x, new_y = x, y - 1
        elif action == "left":
            new_x, new_y = x - 1, y
        elif action == "right":
            new_x, new_y = x + 1, y
        elif action == "pass":
            return True

        # Check if new position is within bounds
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            # Check if the new position is occupied by another agent
            if self.grid[new_y, new_x] == 0:
                # Move the agent to the new position
                self.grid[y, x] = 0  # Clear old position
                self.agent_positions[agent_id] = (new_y, new_x)
                self.grid[new_y, new_x] = agent_id+1  # Mark new position as occupied
                return True
        return False
    
    def move_stag(self, action):
        y, x = self.stag_position
        if action == "up":
            new_x, new_y = x, y + 1
        elif action == "down":
            new_x, new_y = x, y - 1
        elif action == "left":
            new_x, new_y = x - 1, y
        elif action == "right":
            new_x, new_y = x + 1, y

        # Check if new position is within bounds
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            # Check if the new position is occupied by another agent
            if self.grid[new_y, new_x] == 0:
                # Move the agent to the new position
                self.grid[y, x] = 0  # Clear old position
                self.stag_position = (new_y, new_x)
                self.grid[new_y, new_x] = GridWorld.entity2value['stag']  # Mark new position as occupied
                return True
        return False
    
    def check_stag_caught(self):
        y, x = self.stag_position
        hunters = []
        for action in ["up", "down", "left", "right"]:
            if action == "up":
                new_x, new_y = x, y + 1
            elif action == "down":
                new_x, new_y = x, y - 1
            elif action == "left":
                new_x, new_y = x - 1, y
            elif action == "right":
                new_x, new_y = x + 1, y

            # Check if new position is within bounds
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                # Check if the new position is occupied by another agent
                if self.grid[new_y, new_x] == 0:
                    return False, []
                elif 0 < self.grid[new_y, new_x] <= len(self.agent_positions):
                    hunters.append(self.grid[new_y, new_x])
        return True, hunters

    def move_hare(self, action):
        y, x = self.hare_position
        if action == "up":
            new_x, new_y = x, y + 1
        elif action == "down":
            new_x, new_y = x, y - 1
        elif action == "left":
            new_x, new_y = x - 1, y
        elif action == "right":
            new_x, new_y = x + 1, y

        # Check if new position is within bounds
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            # Check if the new position is occupied by another agent
            if self.grid[new_y, new_x] == 0:
                # Move the agent to the new position
                self.grid[y, x] = 0  # Clear old position
                self.hare_position = (new_y, new_x)
                self.grid[new_y, new_x] = GridWorld.entity2value['hare']  # Mark new position as occupied
                return True
        return False
    
    def check_hare_caught(self):
        y, x = self.hare_position
        
        for action in ["up", "down", "left", "right"]:
            if action == "up":
                new_x, new_y = x, y + 1
            elif action == "down":
                new_x, new_y = x, y - 1
            elif action == "left":
                new_x, new_y = x - 1, y
            elif action == "right":
                new_x, new_y = x + 1, y

            # Check if new position is within bounds
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                # Check if the new position is occupied by another agent
                if 0 < self.grid[new_y, new_x] <= len(self.agent_positions):
                    return True, self.grid[new_y, new_x]
        return False, 0

    def get_gen_probs(self):
        prob_dicts = []
        for i in range(len(self.agent_positions)):
            results = {
                'stag': [],
                'hare': []
            }

            gen_probs = {}

            for g in self.generators:
                gen_prob, gen_results = g.prob(
                    agent_id=i,
                    grids=self.grid_history.get_list(), 
                    positions=self.agent_history.get_list(), 
                    stag_positions=self.stag_history.get_list(), 
                    hare_positions=self.hare_history.get_list())
                gen_probs[g.name] = gen_prob
                results[g.target].append(gen_results)

            for targ, targ_res_list in results.items():
                targ_res = np.zeros_like(targ_res_list[0])
                for res in targ_res_list:
                    targ_res = np.logical_or(targ_res, res)
                gen_probs[targ] = gen_probabilities(targ_res)

            prob_dicts.append(gen_probs)
        
        return prob_dicts

    def display_grid(self):
        if self.headless:
            return
        #print('display')
        self.ax[0].clear()
        self.ax[1].clear()
        self.ax[2].clear()

        self.ax[0].imshow(np.logical_not(np.logical_or(self.grid == 0, self.grid != -1)), cmap='binary', interpolation='nearest')

        # Add gridlines
        self.ax[0].grid(color='black', linestyle='-', linewidth=1)
        self.ax[0].set_xticks(np.arange(-.5, self.grid.shape[1], 1), minor=True)
        self.ax[0].set_yticks(np.arange(-.5, self.grid.shape[0], 1), minor=True)
        self.ax[0].grid(which='minor', color='black', linestyle='-', linewidth=1)
        self.ax[0].set_xticks([])
        self.ax[0].set_yticks([])

        for i, pos in enumerate(self.agent_positions):
            self.ax[0].scatter([pos[1]], [pos[0]], label=f'Agent {i}', marker='s', s=150)
        self.ax[0].scatter([self.hare_position[1]], [self.hare_position[0]], label='Hare', marker='d', s=150)
        self.ax[0].scatter([self.stag_position[1]], [self.stag_position[0]], label='Stag', marker='*', s=150)
        self.ax[0].plot([-1, self.width, self.width, -1, -1], [-1, -1, self.height, self.height, -1], c='k')
        self.ax[0].set_xlim(-0.5, self.width-0.5)
        self.ax[0].set_ylim(-0.5, self.height-0.5)


        grid = deepcopy(self.grid)

        gen_probs = {}

        results = {
            'stag': [],
            'hare': []
        }

        for i, g in enumerate(self.generators):
            #print(f'draw generator {i}')
            path, cmds, success = g(np.logical_or(grid == 0, grid == (self.active_agent+1)).astype(int), self.agent_positions[self.active_agent], self.stag_position, self.hare_position)
            if success:
                patharr = np.asarray(path)
                a, b = 0.03, 0.03 * len(self.generators)
                patharr = patharr + np.stack([[0, 0] if j == 0 else [i * 2 * a - b, i * 2 * a - b] for j in range(len(path))])
                self.ax[0].plot(patharr[:, 1], patharr[:, 0], label=f'G{i}: {g.name}')
            else:
                self.ax[0].plot([], [], label=f'G{i}: {g.name}', linestyle='dashed')

            gen_prob, gen_results = g.prob(
                agent_id=self.active_agent,
                grids=self.grid_history.get_list(), 
                positions=self.agent_history.get_list(), 
                stag_positions=self.stag_history.get_list(), 
                hare_positions=self.hare_history.get_list())
            gen_probs[g.name] = gen_prob
            results[g.target].append(gen_results)

        for targ, targ_res_list in results.items():
            targ_res = np.zeros_like(targ_res_list[0])
            for res in targ_res_list:
                targ_res = np.logical_or(targ_res, res)
            gen_probs[targ] = gen_probabilities(targ_res)

        names = list(gen_probs.keys())
        values = list(gen_probs.values())

        self.ax[1].barh(range(len(gen_probs)), values, tick_label=names)

        veracity_vec = self.checker_gen.get_veracity(self, self.active_agent)

        veracity_names = list(veracity_vec.keys())
        veracity_vals = list(veracity_vec.values())

        self.ax[2].barh(range(len(veracity_vec)), veracity_vals, tick_label=veracity_names)

        """cards = ['N', 'S', 'E', 'W']
        for i, (dx, dy) in enumerate([(0, 1), (0, -1), (1, 0), (-1, 0)]):
            #print(f'processing {cards[i]}')
            end = (self.active_target[0] + dy, self.active_target[1] + dx)
            #print(grid[end[1], end[0]])
            if grid[end[1], end[0]] != 0:
                #print('skipping')
                self.ax.plot([], [], label=f'path: {cards[i]}', linestyle='dashed')
                continue
            res = astar(grid, start, end)
            if res is not None:
                path = np.asarray(res)
                #path = path + np.random.normal(loc=0, scale=0.05, size=path.shape) * np.stack([[0, 0] if j == 0 else [1, 1] for j in range(len(res))])
                a, b = 0.03, 0.09
                path = path + np.stack([[0, 0] if j == 0 else [i * 2 * a - b, i * 2 * a - b] for j in range(len(res))])
                self.ax.plot(path[:, 1], path[:, 0], label=f'path: {cards[i]}', linestyle='dashed')"""

        self.ax[0].legend(loc='upper center', bbox_to_anchor=( 0.5, 1.2),
          fancybox=True, shadow=True, ncol=2)
        
        plt.draw()

    def tick(self):
        #print('tick')
        actions = ["up", "down", "left", "right", "pass"]
        veracities = []
        for i, a in enumerate(self.actors):
            #print(f'agent {i} acting')
            grid = deepcopy(self.grid)
            masked_grid = np.logical_or(grid == 0, grid == (i+1)).astype(int)
            agent_pos = self.agent_positions[i]
            other_poses = [p for j, p in enumerate(self.agent_positions) if j != i]
            veracity_vec = self.checker_gen.get_veracity(self, i)
            cmd, gen = a(veracity_vec, actions, masked_grid, self.stag_position, self.hare_position, agent_pos, other_poses)
            veracity_vec['Generator'] = gen
            veracities.append(veracity_vec)
            self.move_agent(cmd, i)
        
        stag_caught, hunters = self.check_stag_caught()
        if stag_caught:
            #print(f'{hunters} caught the stag!')
            self.grid[self.stag_position] = 0
            open_spaces = np.argwhere(self.grid == 0)
            new_positions = [(p[0], p[1]) for p in open_spaces[np.random.choice(len(open_spaces), 1, replace=False)]]
            self.stag_position = new_positions[0]
            self.grid[self.stag_position] = GridWorld.entity2value['stag']

        hare_caught, hunter = self.check_hare_caught()
        if hare_caught:
            #print(f'{hunter} caught the hare!')
            self.grid[self.hare_position] = 0
            open_spaces = np.argwhere(self.grid == 0)
            new_positions = [(p[0], p[1]) for p in open_spaces[np.random.choice(len(open_spaces), 1, replace=False)]]
            self.hare_position = new_positions[0]
            self.grid[self.hare_position] = GridWorld.entity2value['hare']

        if self.step % 3 == 2:
            cmds = ['up', 'down', 'left', 'right']
            random.shuffle(cmds)

            for cmd in cmds:
                move_success = self.move_stag(cmd)
                if move_success:
                    break

        if self.step % 2 == 1:
            for i in range(2):
                cmd = (['up', 'down', 'left', 'right'])[np.random.choice(4)]
                self.move_hare(cmd)

        self.step += 1
        return veracities

    def on_key_press(self, event):
        if event.key == 'up':
            self.move_agent('up', self.active_agent)
        elif event.key == 'down':
            self.move_agent('down', self.active_agent)
        elif event.key == 'left':
            self.move_agent('left', self.active_agent)
        elif event.key == 'right':
            self.move_agent('right', self.active_agent)
        elif event.key == 'c':
            self.active_agent = (self.active_agent + 1) % len(self.agent_positions)
        elif event.key == 'v':
            self.active_target = self.stag_position
        elif event.key == 'b':
            self.active_target = self.hare_position
        elif event.key in '01234567':
            grid = deepcopy(self.grid)
            _, cmds, success = self.generators[int(event.key)](np.logical_or(grid == 0, grid == (self.active_agent+1)).astype(int), self.agent_positions[self.active_agent], self.stag_position, self.hare_position)
            if success:
                for cmd in cmds:
                    #print(cmd)
                    self.move_agent(cmd, self.active_agent)
                    break
                print(f'Generator {event.key} Success! :D')
            else:
                print(f'Generator {event.key} Failed! :\'(')
        elif event.key == 't':
            self.tick()
        elif event.key == 'p':
            print(f'\n\n{self.grid}\n\n')
        else:
            print(event.key)
        self.add_history()
        self.display_grid()