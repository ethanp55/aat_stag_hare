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
class SingleGenModel(Model):
    def __init__(self, aat_dim: int, state_dim: int) -> None:
        super(SingleGenModel, self).__init__()
        self.aat_dim = aat_dim
        self.state_dim = state_dim

        self.dense_aat_1 = Dense(self.aat_dim, activation='relu')
        self.dense_aat_2 = Dense(self.state_dim, activation='relu')

        self.dense_state_1 = Dense(self.state_dim, activation='relu')
        self.dense_state_2 = Dense(self.state_dim, activation='relu')

        self.dense_combined_1 = Dense(self.state_dim, activation='relu')
        self.dense_combined_2 = Dense(32, activation='relu')

        self.output_layer = Dense(1, activation='linear')

    def get_config(self):
        return {'state_dim': self.state_dim, 'aat_dim': self.aat_dim}

    def call(self, states: Tuple[np.array, np.array], return_transformed_state: bool = False) -> tf.Tensor:
        aat_state, state = states

        x_aat = self.dense_aat_1(aat_state)
        x_aat = x_aat + aat_state
        x_aat = self.dense_aat_2(x_aat)

        x_state = self.dense_state_1(state)
        x_state = x_state + state
        x_state = self.dense_state_2(x_state)

        x = x_aat + x_state
        x = x + self.dense_combined_1(x)
        x = self.dense_combined_2(x)

        if return_transformed_state:
            return x

        return self.output_layer(x)


class SMAlegAATr(Agent):
    def __init__(self, name: str = 'SMAlegAATr', train: bool = False, enhanced: bool = False) -> None:
        Agent.__init__(self, name)
        self.generator_pool = GeneratorPool(name, check_assumptions=True, no_baseline_labels=True)
        self.generator_indices = [i for i in range(len(self.generator_pool.generators))]
        self.generator_to_use_idx = None
        file_adj = '_enh' if enhanced else ''
        self.model = load_model(f'../aat/single_gen_model/single_gen_model{file_adj}.keras')
        self.scaler = pickle.load(open(f'../aat/single_gen_model/single_gen_scaler{file_adj}.pickle', 'rb'))
        self.aat_scaler = pickle.load(open(f'../aat/single_gen_model/single_gen_scaler_aat{file_adj}.pickle', 'rb'))
        self.train = train
        self.tracked_vector = None
        self.generators_used = set()
        self.prev_reward = None

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        self.prev_reward = reward

        # Get the actions of every generator
        generator_to_token_allocs = self.generator_pool.act(state, reward, round_num, self.generator_to_use_idx)

        # State vector
        curr_state = state.vector_representation(self.name)
        curr_state = self.scaler.transform(curr_state.reshape(1, -1))

        # Make predictions for each generator
        best_pred, best_generator_idx, best_vector = -np.inf, None, None

        for generator_idx in self.generator_indices:
            aat_vec = np.array(self.generator_pool.assumptions(generator_idx)).reshape(-1, 1)
            n_zeroes = 12 - aat_vec.shape[0]
            aat_vec = np.append(aat_vec, np.zeros(n_zeroes)).reshape(1, -1)
            aat_vec = self.aat_scaler.transform(aat_vec.reshape(1, -1))
            pred = self.model((aat_vec, curr_state)).numpy()[0][0]

            if pred > best_pred:
                best_pred, best_generator_idx = pred, generator_idx
                best_vector = self.model((aat_vec, curr_state), return_transformed_state=True).numpy()

        self.generator_to_use_idx = best_generator_idx
        self.tracked_vector = best_vector.reshape(-1, )
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
