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


class NN(keras.Model):
    def __init__(self, state_dim: int, action_dim: int) -> None:
        super(NN, self).__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim

        self.dense1 = keras.layers.Dense(self.state_dim, activation='relu')
        self.dense2 = keras.layers.Dense(32, activation='relu')
        self.output_layer = keras.layers.Dense(self.action_dim, activation='softmax')

    def get_config(self):
        return {'state_dim': self.state_dim, 'action_dim': self.action_dim}

    def call(self, state: np.array, return_transformed_state: bool = False) -> tf.Tensor:
        x = self.dense1(state)
        x = self.dense2(x)

        if return_transformed_state:
            return x

        return self.output_layer(x)


class PPO(Agent):
    def __init__(self, name: str = 'PPO', discount_factor: float = 0.9, replay_buffer_size: int = 50000,
                 train_network: bool = False) -> None:
        Agent.__init__(self, name)
        # Variables used for training and/or action selection
        self.discount_factor = discount_factor
        self.train_network = train_network
        self.prev_reward = 0
        self.best_loss = np.inf

        # Generators
        self.generator_pool = GeneratorPool(name)
        self.generator_indices = [i for i in range(len(self.generator_pool.generators))]
        self.generator_to_use_idx = None

        # Action and value models
        self.state_dim = 14
        self.action_dim = len(self.generator_indices)
        self.action_model = NN(self.state_dim, self.action_dim)
        self.value_model = keras.Sequential([
            keras.layers.Dense(self.state_dim, activation='relu'),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(1)
        ])

        # Optimizers
        self.action_model_optimizer = tf.optimizers.Adam(learning_rate=3e-4)
        self.value_model_optimizer = tf.optimizers.Adam(learning_rate=1e-3)

        # Replay buffer
        self.replay_buffer = deque(maxlen=replay_buffer_size)

        # Episode experiences (to add to the replay buffer)
        self.current_episode_experiences = []

        # State scaler
        self.scaler = DynamicMinMaxScaler(self.state_dim)

        # If we're not in training mode, load the saved/trained model
        if not self.train_network:
            self.load_network()

        self.tracked_vector = None
        self.generators_used = set()

    def reset(self) -> None:
        self.generator_to_use_idx = None
        self.prev_reward = 0
        self.generators_used.clear()

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        # Get the actions of every generator
        generator_to_token_allocs = self.generator_pool.act(state, reward, round_num, self.generator_to_use_idx)

        curr_state = state.vector_representation(self.name)

        scaled_state = self.scaler.scale(curr_state)
        prob_weights = self.action_model(np.expand_dims(scaled_state, 0))
        self.generator_to_use_idx = np.random.choice(len(self.generator_indices), p=np.squeeze(prob_weights))

        network_state = self.action_model(np.expand_dims(scaled_state, 0), return_transformed_state=True)
        self.tracked_vector = network_state.numpy().reshape(-1, )

        if self.train_network:
            increase = reward - self.prev_reward
            value = self.value_model(np.expand_dims(scaled_state, 0)).numpy()[0][0]
            done = state.hare_captured() or state.stag_captured()
            self.add_experience(self.generator_to_use_idx, increase, curr_state, prob_weights.numpy(), value, done)
        self.prev_reward = reward

        self.generators_used.add(self.generator_to_use_idx)

        token_allocations = generator_to_token_allocs[self.generator_to_use_idx]

        # if state.hare_captured() or state.stag_captured():
        #     print(f'Generators used: {self.generators_used}')

        return token_allocations

    def is_hunting_hare(self) -> bool:
        return self.generator_pool.hunting_hare(self.generator_to_use_idx)

    def train(self) -> None:
        # Extract historical data
        batch = random.sample(self.replay_buffer, len(self.replay_buffer))
        batch_states, batch_actions, batch_old_log_probs, batch_values, batch_rewards, batch_dones = map(np.array, zip(*batch))
        actions_taken = tf.convert_to_tensor(batch_actions, dtype=tf.int32)

        # Calculate advantages and discounted rewards
        def _discount_rewards(rewards):
            new_rewards = [rewards[-1]]
            for i in reversed(range(len(rewards) - 1)):
                new_rewards.append(rewards[i] + self.discount_factor * new_rewards[-1])
            return np.array(new_rewards[::-1])
        next_values = np.concatenate([batch_values[1:], [0]])
        deltas = [rew + self.discount_factor * next_val - val for rew, val, next_val in zip(batch_rewards, batch_values, next_values)]
        gaes = [deltas[-1]]
        for i in reversed(range(len(deltas) - 1)):
            gaes.append(deltas[i] + 0.97 * self.discount_factor * gaes[-1])
        gaes = np.array(gaes[::-1])
        gaes = (gaes - gaes.mean()) / (gaes.std() + 1e-8)
        returns = _discount_rewards(batch_rewards)

        # Train the action/policy model
        for _ in range(100):
            with tf.GradientTape() as tape:
                new_probs = self.action_model(batch_states)
                new_log_probs = tf.math.log(new_probs + 1e-10)
                old_log_probs_for_actions = tf.gather(batch_old_log_probs, actions_taken, batch_dims=1)
                new_log_probs_for_actions = tf.gather(new_log_probs, actions_taken, batch_dims=1)
                ratio = tf.math.exp(new_log_probs_for_actions - old_log_probs_for_actions)
                clipped_ratio = tf.clip_by_value(ratio, 1 - 0.2, 1 + 0.2)
                policy_loss = -tf.reduce_mean(tf.minimum(ratio * gaes, clipped_ratio * gaes))

                kl = tf.reduce_mean(old_log_probs_for_actions - new_log_probs_for_actions).numpy()
                if kl > 0.01:
                    print(f'KL too large: {kl}')
                    break

            grads = tape.gradient(policy_loss, self.action_model.trainable_variables)
            self.action_model_optimizer.apply_gradients(zip(grads, self.action_model.trainable_variables))
            # loss_val = policy_loss.numpy()
            # if loss_val < self.best_loss:
            #     print(f'Loss improved from {self.best_loss} to {loss_val}')
            #     self.best_loss = loss_val
            #     self.save_network()
        self.save_network()

        # Train the value model
        for _ in range(100):
            with tf.GradientTape() as tape:
                value_loss = tf.reduce_mean((returns - self.value_model(batch_states)) ** 2)

            grads = tape.gradient(value_loss, self.value_model.trainable_variables)
            self.value_model_optimizer.apply_gradients(zip(grads, self.value_model.trainable_variables))

    def add_experience(self, action: int, reward: float, state: np.array, probs: np.array, value: float, done: bool) -> None:
        # Accumulate experiences over multiple time steps
        self.scaler.update(state)
        scaled_state = self.scaler.scale(state)
        log_probs = np.log(np.squeeze(probs) + 1e-10)
        self.current_episode_experiences.append((scaled_state, action, log_probs, value, reward, done))

        # If the episode is done, add the accumulated experiences to the replay buffer
        if done:
            self.replay_buffer.extend(self.current_episode_experiences)
            self.current_episode_experiences = []

    def clear_buffer(self) -> None:
        self.replay_buffer.clear()
        self.current_episode_experiences = []

    def save_network(self) -> None:
        # Save the network and scaler
        self.action_model.save('../agents/ppo_model/model.keras')

        with open('../agents/ppo_model/scaler.pickle', 'wb') as f:
            pickle.dump(self.scaler, f)

    def load_network(self) -> None:
        # Load the network and scaler
        self.action_model = keras.models.load_model('../agents/ppo_model/model.keras')
        self.scaler = pickle.load(open('../agents/ppo_model/scaler.pickle', 'rb'))
