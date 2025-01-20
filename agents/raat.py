from agents.agent import Agent
from agents.generator_pool import GeneratorPool
from environment.state import State
import keras
import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import load_model, Model
from typing import Tuple


@keras.saving.register_keras_serializable()
class AATNetwork(Model):
    def __init__(self, aat_dim: int) -> None:
        super(AATNetwork, self).__init__()
        self.aat_dim = aat_dim

        self.dense1 = Dense(self.aat_dim, activation='relu')
        self.dense2 = Dense(32, activation='relu')
        self.output_layer = Dense(4, activation='linear')

    def get_config(self):
        return {'aat_dim': self.aat_dim}

    def call(self, aat_state: np.array, return_transformed_state: bool = False) -> tf.Tensor:
        x = self.dense1(aat_state)
        x = self.dense2(x)

        if return_transformed_state:
            return x

        return self.output_layer(x)


class RAAT(Agent):
    def __init__(self, name: str = 'RAAT', train: bool = False, enhanced: bool = False) -> None:
        Agent.__init__(self, name)
        self.generator_pool = GeneratorPool(name, check_assumptions=True, no_baseline_labels=True)
        self.generator_indices = [i for i in range(len(self.generator_pool.generators))]
        self.generator_to_use_idx = None
        file_adj = '_enh' if enhanced else ''
        self.model = load_model(f'../aat/aat_network/aat_network_model{file_adj}.keras')
        self.aat_scaler = pickle.load(open(f'../aat/aat_network/aat_network_scaler{file_adj}.pickle', 'rb'))
        self.train = train
        self.tracked_vector = None
        self.generators_used = set()
        self.prev_reward = None

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        self.prev_reward = reward

        # Get the actions of every generator
        generator_to_token_allocs = self.generator_pool.act(state, reward, round_num, self.generator_to_use_idx)

        # AAT vector
        aat_vec = []
        for i in self.generator_indices:
            aat_vec.extend(self.generator_pool.assumptions(i))
        aat_vec = np.array(aat_vec).reshape(1, -1)
        aat_vec = self.aat_scaler.transform(aat_vec)

        # Make predictions
        q_values = self.model(aat_vec)
        self.generator_to_use_idx = np.argmax(q_values.numpy())
        self.tracked_vector = self.model(aat_vec, return_transformed_state=True).numpy().reshape(-1, )
        self.generators_used.add(self.generator_to_use_idx)

        token_allocations = generator_to_token_allocs[self.generator_to_use_idx]

        # If we're done and are supposed to train AAT, do so
        done = state.hare_captured() or state.stag_captured()
        if done and self.train:
            self.generator_pool.train_aat(enhanced=True)
        # if done:
        #     print(f'Generators used: {self.generators_used}')

        return token_allocations

    def is_hunting_hare(self) -> bool:
        return self.generator_pool.hunting_hare(self.generator_to_use_idx)
