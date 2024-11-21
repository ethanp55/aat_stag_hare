import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
import os
from sklearn.manifold import TSNE
from typing import List


def _plot_embeddings(labels: List[str], embeddings: np.array, agent_name: str, three_dimensions: bool = False) -> None:
    labels = np.array(labels)
    unique_labels = np.unique(labels)
    colors = plt.get_cmap('tab20')(Normalize()(unique_labels))
    # fig = plt.figure(figsize=(15, 15))
    # plt.grid()
    fig = plt.figure(figsize=(3, 3))

    if three_dimensions:
        ax = fig.add_subplot(111, projection='3d')

        for j, label in enumerate(unique_labels):
            label_points = embeddings[labels == label]
            ax.scatter(label_points[:, 0], label_points[:, 1], label_points[:, 2], s=10, alpha=1.0, color=colors[j],
                       label=label)

    else:
        for j, label in enumerate(unique_labels):
            label_points = embeddings[labels == label]
            plt.scatter(label_points[:, 0], label_points[:, 1], s=10, alpha=1.0, color=colors[j], label=label)

    # plt.legend(loc='best', fontsize='18')
    plt.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, left=False, right=False,
                    labelleft=False)

    image_name_adj = '_3d' if three_dimensions else ''
    plt.savefig(f'../simulations/vector_plots/{agent_name}{image_name_adj}.png', bbox_inches='tight')
    plt.clf()


folder = '../simulations/vectors/'
gen_vectors = {}
agents_to_ignore = ['AleqgAATr', 'RDQN', 'MADQN', 'RAlegAATr', 'SOAleqgAATr', 'DQN']  # Agents that converged to output the same vector, regardless of state

for file in os.listdir(folder):
    agent_name = file.split('_')[0]
    if agent_name in agents_to_ignore:
        continue
    file_path = f'{folder}{file}'
    data = np.genfromtxt(file_path, delimiter=',', skip_header=0)
    if len(data.shape) == 1:
        data = data.reshape(1, -1)
    generators, vectors = data[:, 0], data[:, 1:]
    assert generators.shape[0] == vectors.shape[0]

    for i in range(generators.shape[0]):
        generator_idx = int(generators[i])
        agent_data = gen_vectors.get(agent_name, {})
        agent_data[generator_idx] = agent_data.get(generator_idx, []) + [vectors[i, :]]
        gen_vectors[agent_name] = agent_data

for agent_name, agent_data in gen_vectors.items():
    print(agent_name)
    all_labels, all_vectors = [], None

    for key, vector_list in agent_data.items():
        all_labels.extend([key] * len(vector_list))
        all_vectors = np.array(vector_list) if all_vectors is None else np.concatenate(
            [all_vectors, np.array(vector_list)])

    for three_dimensions in [False]:
        n_components = 3 if three_dimensions else 2
        all_embeddings = TSNE(n_components=n_components).fit_transform(all_vectors)
        _plot_embeddings(all_labels, all_embeddings, agent_name, three_dimensions=three_dimensions)
