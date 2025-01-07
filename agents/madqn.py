from agents.agent import Agent
from agents.generator_pool import GeneratorPool
from collections import deque
from environment.state import State
import numpy as np
import pickle
import random
import tensorflow as tf
from tensorflow import keras
from typing import Tuple


class DynamicMinMaxScaler:
    def __init__(self, num_features: int) -> None:
        self.num_features = num_features
        self.min_vals = np.inf * np.ones(num_features)
        self.max_vals = -np.inf * np.ones(num_features)

    def update(self, state: np.array) -> None:
        self.min_vals = np.minimum(self.min_vals, state)
        self.max_vals = np.maximum(self.max_vals, state)

    def scale(self, state: np.array) -> np.array:
        return (state - self.min_vals) / (self.max_vals - self.min_vals + 0.00001)


class DQN(keras.Model):
    def __init__(self, state_dim: int, action_dim: int) -> None:
        super(DQN, self).__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim

        self.dense1 = keras.layers.Dense(self.state_dim, activation='relu')
        self.dense2 = keras.layers.Dense(32, activation='relu')
        self.output_layer = keras.layers.Dense(self.action_dim, activation='linear')

    def get_config(self):
        return {'state_dim': self.state_dim, 'action_dim': self.action_dim}

    def call(self, state: np.array, return_transformed_state: bool = False) -> tf.Tensor:
        x = self.dense1(state)
        x = self.dense2(x)

        if return_transformed_state:
            return x

        return self.output_layer(x)


class MADQN(Agent):
    def __init__(self, name: str = 'MADQN', learning_rate: float = 0.001, discount_factor: float = 0.9,
                 epsilon: float = 0.1, epsilon_decay: float = 0.99, replay_buffer_size: int = 50000,
                 batch_size: int = 32, train_networks: bool = False) -> None:
        Agent.__init__(self, name)
        # Generators
        self.generator_pool = GeneratorPool(name)
        self.generator_indices = [i for i in range(len(self.generator_pool.generators))]
        self.generator_to_use_idx = None

        # Variables used for training and/or action selection
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.state = None
        self.train_networks = train_networks
        self.prev_reward = 0
        self.best_losses = [np.inf for _ in self.generator_indices]

        # DQN model and target model
        self.state_dim = 14
        self.action_dim = 1
        self.models = [DQN(self.state_dim, self.action_dim) for _ in self.generator_indices]
        self.target_models = [DQN(self.state_dim, self.action_dim) for _ in self.generator_indices]
        for i in self.generator_indices:
            model, target_model = self.models[i], self.target_models[i]
            target_model.set_weights(model.get_weights())

        # Optimizers
        self.optimizers = [tf.optimizers.Adam(learning_rate=learning_rate) for _ in self.generator_indices]

        # Replay buffer
        self.replay_buffers = [deque(maxlen=replay_buffer_size) for _ in self.generator_indices]

        # Episode experiences (to add to the replay buffers)
        self.current_episode_experiences = [[] for _ in self.generator_indices]

        # State scaler
        self.scalers = [DynamicMinMaxScaler(self.state_dim) for _ in self.generator_indices]

        # If we're not in training mode, load the saved/trained models
        if not self.train_networks:
            self.load_networks()

        self.tracked_vector = None
        self.generators_used = set()

    def update_epsilon(self) -> None:
        self.epsilon *= self.epsilon_decay

    def reset(self) -> None:
        self.generator_to_use_idx = None
        self.prev_reward = 0
        self.state = None

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        # Add a new experience to the replay buffer and update the network weights (if there are enough experiences)
        if self.train_networks and self.state is not None:
            increase = reward - self.prev_reward
            done = state.hare_captured() or state.stag_captured()
            self.add_experience(self.generator_to_use_idx, increase, state.vector_representation(self.name), done)
        self.prev_reward = reward

        # Get the actions of every generator
        generator_to_token_allocs = self.generator_pool.act(state, reward, round_num, self.generator_to_use_idx)

        self.state = state.vector_representation(self.name)

        # Epsilon-greedy policy for generator selection (only consider exploring if we're in training mode)
        if self.train_networks and np.random.rand() < self.epsilon:
            self.generator_to_use_idx = np.random.choice(self.generator_indices)

        else:
            q_vals, vectors = [], []

            for i in self.generator_indices:
                scaled_state = self.scalers[i].scale(self.state)
                q_values = self.models[i](np.expand_dims(scaled_state, 0))
                q_vals.append(q_values.numpy())

                vec = self.models[i](np.expand_dims(scaled_state, 0), return_transformed_state=True)
                vectors.append(vec.numpy().reshape(-1, ))

            self.generator_to_use_idx = np.argmax(q_vals)
            self.tracked_vector = vectors[self.generator_to_use_idx]

        self.generators_used.add(self.generator_to_use_idx)

        token_allocations = generator_to_token_allocs[self.generator_to_use_idx]

        # if state.hare_captured() or state.stag_captured():
        #     print(f'Generators used: {self.generators_used}')

        return token_allocations

    def train(self) -> None:
        for i in self.generator_indices:
            batch_size = min(len(self.replay_buffers[i]), self.batch_size)
            if batch_size <= 1:
                continue

            model, target_model, optimizer = self.models[i], self.target_models[i], self.optimizers[i]

            for _ in range(100):
                best_loss = self.best_losses[i]

                # Sample a batch of experiences from the replay buffer
                batch = random.sample(self.replay_buffers[i], batch_size)
                batch_states, batch_rewards, batch_next_states, batch_dones = map(np.array, zip(*batch))

                # Q-learning update using the DQN loss
                next_q_values = target_model(batch_next_states)
                targets = batch_rewards + (1 - batch_dones) * self.discount_factor * tf.squeeze(next_q_values)

                with tf.GradientTape() as tape:
                    q_values = model(batch_states)
                    loss = tf.keras.losses.MSE(targets, tf.squeeze(q_values))

                loss_val = loss.numpy()
                if loss_val < best_loss:
                    print(f'Loss {i} improved from {best_loss} to {loss_val}')
                    self.best_losses[i] = loss_val
                    self.save_networks()

                gradients = tape.gradient(loss, model.trainable_variables)
                optimizer.apply_gradients(zip(gradients, model.trainable_variables))

            target_model.set_weights(model.get_weights())

    def add_experience(self, action: int, reward: float, next_state: np.array, done: bool):
        # Accumulate experiences over multiple time steps
        scaled_state = self.scalers[action].scale(self.state)
        scaled_next_state = self.scalers[action].scale(next_state)
        self.scalers[action].update(next_state)

        self.current_episode_experiences[action].append((scaled_state, reward, scaled_next_state, done))

        # If the episode is done, add the accumulated experiences to the replay buffers
        if done:
            for i in self.generator_indices:
                self.replay_buffers[i].extend(self.current_episode_experiences[i])
                self.current_episode_experiences[i] = []

    def clear_buffer(self) -> None:
        for i in self.generator_indices:
            self.replay_buffers[i].clear()
            self.current_episode_experiences[i] = []

    def save_networks(self) -> None:
        # Save the networks and scalers
        for i in range(len(self.generator_indices)):
            self.models[i].save(f'../agents/madqn_model/model_{i}.keras')

            with open(f'../agents/madqn_model/scaler_{i}.pickle', 'wb') as f:
                pickle.dump(self.scalers[i], f)

    def load_networks(self) -> None:
        # Load the networks and scalers
        self.models, self.scalers = [], []

        for i in range(len(self.generator_indices)):
            self.models.append(keras.models.load_model(f'../agents/madqn_model/model_{i}.keras'))
            self.scalers.append(pickle.load(open(f'../agents/madqn_model/scaler_{i}.pickle', 'rb')))
