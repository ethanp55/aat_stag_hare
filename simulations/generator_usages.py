import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

folder = '../simulations/generator_usage/'
files = os.listdir(folder)
agent_names = set()
N_GENERATORS = 4

for file in files:
    agent_name = file.split('_')[0]
    agent_names.add(agent_name)

for agent_name in agent_names:
    grid_sizes, opponent_types = [], []
    list_of_generator_counts = [[] for _ in range(N_GENERATORS)]

    for file in files:
        name = file.split('_')[0]
        if name != agent_name:
            continue
        height = file.split('h=')[1].split('_')[0]
        width = file.split('w=')[1].split('.')[0]
        opp_type = file[len(agent_name) + 1:].split('_')[0]
        data = np.genfromtxt(f'{folder}{file}', delimiter=',', skip_header=1)
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        curr_generator_counts = {}

        for row in data:
            generator = row[-1]
            curr_generator_counts[generator] = curr_generator_counts.get(generator, 0) + 1

        for i in range(N_GENERATORS):
            gen_count = curr_generator_counts.get(i, 0)
            list_of_generator_counts[i].append(gen_count)

        grid_sizes.append(f'{height}_{width}')
        opponent_types.append(opp_type)

    data_dict = {
        'grid_sizes': grid_sizes,
        'opponent_type': opponent_types,
    }
    for i in range(N_GENERATORS):
        data_dict[f'generator_{i}'] = list_of_generator_counts[i]

    df = pd.DataFrame(data_dict)

    # Plot generator usages by grid dimensions
    df_melted = pd.melt(df, id_vars=['grid_sizes'], value_vars=[f'generator_{i}' for i in range(N_GENERATORS)],
                        var_name='generator', value_name='usage_count')
    df_grouped = df_melted.groupby(['grid_sizes', 'generator']).sum().reset_index()
    unique_grid_sizes = df_grouped['grid_sizes'].unique()
    bar_positions = np.arange(len(df_grouped['generator'].unique()))
    bar_width = 0.2
    fig, ax = plt.subplots()
    for i, size in enumerate(unique_grid_sizes):
        subset = df_grouped[df_grouped['grid_sizes'] == size]
        ax.bar(bar_positions + i * bar_width, subset['usage_count'], bar_width, label=f'size={size}')
    ax.set_xticks(bar_positions + bar_width * (len(unique_grid_sizes) - 1) / 2)
    ax.set_xticklabels([i for i in range(N_GENERATORS)])
    ax.set_xlabel('Generator')
    ax.set_ylabel('Usage Count')
    ax.legend()
    plt.grid()
    plt.savefig(f'../simulations/generator_usage_plots/{agent_name}_grid_sizes.png', bbox_inches='tight')
    plt.clf()

    # Overall
    generator_usage = df[[f'generator_{i}' for i in range(N_GENERATORS)]].sum()
    plt.figure(figsize=(10, 3))
    plt.grid()
    plt.bar(generator_usage.index, generator_usage.values)
    plt.xticks(ticks=range(N_GENERATORS), labels=['Greedy-Hare', 'Greedy Planner-Hare', 'Greedy Planner-Stag',
                                                  'Team Aware'])
    plt.xlabel('Generator', fontsize=18, fontweight='bold')
    plt.ylabel('Counts', fontsize=18, fontweight='bold')
    plt.savefig(f'../simulations/generator_usage_plots/{agent_name}_overall.png', bbox_inches='tight')
    plt.clf()
