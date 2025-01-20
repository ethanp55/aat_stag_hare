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
class SingleGenModelRaw(Model):
    def __init__(self, state_dim: int) -> None:
        super(SingleGenModelRaw, self).__init__()
        self.state_dim = state_dim

        self.dense1 = Dense(self.state_dim, activation='relu')
        self.dense2 = Dense(32, activation='relu')
        self.output_layer = Dense(4, activation='linear')

    def get_config(self):
        return {'state_dim': self.state_dim}

    def call(self, state: np.array, return_transformed_state: bool = False) -> tf.Tensor:
        x = self.dense1(state)
        x = self.dense2(x)

        if return_transformed_state:
            return x

        return self.output_layer(x)


class RawO(Agent):
    def __init__(self, name: str = 'RawO', train: bool = False, enhanced: bool = False) -> None:
        Agent.__init__(self, name)
        self.generator_pool = GeneratorPool(name, check_assumptions=True, no_baseline_labels=True)
        self.generator_indices = [i for i in range(len(self.generator_pool.generators))]
        self.generator_to_use_idx = None
        file_adj = '_enh' if enhanced else ''
        self.model = load_model(f'../aat/single_gen_model_raw/single_gen_model{file_adj}.keras')
        self.scaler = pickle.load(open(f'../aat/single_gen_model_raw/single_gen_scaler{file_adj}.pickle', 'rb'))
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

        # Make predictions
        q_values = self.model(curr_state)
        self.generator_to_use_idx = np.argmax(q_values.numpy())
        self.tracked_vector = self.model(curr_state, return_transformed_state=True).numpy().reshape(-1, )
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
