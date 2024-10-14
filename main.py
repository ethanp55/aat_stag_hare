import matplotlib.pyplot as plt
import argparse
from tqdm import tqdm
import pandas as pd

from world import GridWorld

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-wd", "--width", type=int, default=10, 
        help="Width of the grid")
    parser.add_argument("-ht", "--height", type=int, default=10, 
        help="Height of the grid")
    parser.add_argument("-na", "--num_agents", type=int, default=3, 
        help="Number of agents to spawn")
    parser.add_argument("-t", "--train", action="store_true")
    args = parser.parse_args()
    grid_world = GridWorld(width=args.width, height=args.height, num_agents=args.num_agents, headless=args.train)

    if args.train:
        all_veracities = []
        for _ in tqdm(range(500)):
            all_veracities.extend(grid_world.tick())

        df = pd.DataFrame(all_veracities)
        for c in df.columns:
            if c != 'Generator':
                df[c] = df[c].astype(float)
        df.to_csv('./data.csv', index=False)
        
