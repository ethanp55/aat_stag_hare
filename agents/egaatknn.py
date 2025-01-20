from agents.agent import Agent
from agents.generator_pool import GeneratorPool
from environment.state import State
import numpy as np
import pickle
from typing import Tuple
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler


class EGAATKNN(Agent):
    def __init__(self, name: str = 'EGAATKNN', train_knn: bool = False, epsilon: float = 0.1, epsilon_decay: float = 0.99) -> None:
        Agent.__init__(self, name)
        self.generator_pool = GeneratorPool(name, check_assumptions=True)
        self.generator_indices = [i for i in range(len(self.generator_pool.generators))]
        self.generator_to_use_idx = None
        self.train_knn = train_knn
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.models = {}
        self.scalers = {}
        if not self.train_knn:
            for generator_idx in self.generator_indices:
                knn_path = f'../agents/egaatknn/generator_{generator_idx}_knn.pickle'
                scaler_path = f'../agents/egaatknn/generator_{generator_idx}_scaler.pickle'
                self.models[generator_idx] = pickle.load(open(knn_path, 'rb'))
                self.scalers[generator_idx] = pickle.load(open(scaler_path, 'rb'))
        self.tracked_vector = None
        self.generators_used = set()
        self.training_data, self.reward_history = {}, []
        self.x_data, self.y_data = {}, {}
        self.prev_state = None

    def update_epsilon(self) -> None:
        self.epsilon *= self.epsilon_decay

    def reset(self) -> None:
        self.generator_to_use_idx = None
        self.prev_state = None
        self.training_data, self.reward_history = {}, []
        self.generator_pool = GeneratorPool(self.name, check_assumptions=True)

    def clear_buffer(self) -> None:
        self.reset()
        self.x_data, self.y_data = {}, {}

    def train(self, n_folds=5) -> None:
        for generator_idx in self.generator_indices:
            if generator_idx not in self.x_data:
                continue
            aat_vecs, labels = self.x_data[generator_idx], self.y_data[generator_idx]
            assert len(aat_vecs) == len(labels)
            if len(aat_vecs) < n_folds:
                continue

            x, y = np.array(aat_vecs), np.array(labels)
            scaler = StandardScaler()
            x_scaled = scaler.fit_transform(x)

            print(f'X and Y data for generator {generator_idx}')
            print('X train shape: ' + str(x_scaled.shape))
            print('Y train shape: ' + str(y.shape))

            # Use cross validation (10 folds) to find the best k value
            k_values, cv_scores = range(1, int(len(x_scaled) ** 0.5) + 1), []
            for k in k_values:
                knn = KNeighborsRegressor(n_neighbors=k, weights='distance')
                scores = cross_val_score(knn, x_scaled, y, cv=5, scoring='neg_mean_squared_error')
                cv_scores.append(scores.mean())
            n_neighbors = k_values[np.argmax(cv_scores)]

            # Create and store the model
            knn = KNeighborsRegressor(n_neighbors=n_neighbors, weights='distance')
            knn.fit(x_scaled, y)

            with open(f'../agents/egaatknn/generator_{generator_idx}_knn.pickle', 'wb') as f:
                pickle.dump(knn, f)

            with open(f'../agents/egaatknn/generator_{generator_idx}_scaler.pickle', 'wb') as f:
                pickle.dump(scaler, f)

            self.models[generator_idx] = knn
            self.scalers[generator_idx] = scaler

            # Print metrics and best number of neighbors
            print(f'Best MSE: {-cv_scores[np.argmax(cv_scores)]}')
            print(f'Best R-squared: {r2_score(y, knn.predict(x_scaled))}')
            print(f'N neighbors: {n_neighbors}\n')

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        # Update training data, if we are supposed to train
        if self.train_knn and self.prev_state is not None:
            assert self.generator_to_use_idx is not None
            aat_vec = np.array(self.generator_pool.assumptions(self.generator_to_use_idx))
            tup = (aat_vec, round_num)
            self.training_data[self.generator_to_use_idx] = self.training_data.get(self.generator_to_use_idx, []) + [tup]
        self.reward_history.append(reward)
        self.prev_state = state

        # Get the actions of every generator
        generator_to_token_allocs = self.generator_pool.act(state, reward, round_num, self.generator_to_use_idx)

        # Make predictions for each generator
        best_pred, best_generator_idx, best_vector = -np.inf, None, None

        if len(self.models) == 0:  # First phase of training
            assert self.train_knn
            best_generator_idx = np.random.choice(self.generator_indices)

        elif self.train_knn and np.random.rand() < self.epsilon:
            best_generator_idx = np.random.choice(self.generator_indices)

        else:
            for generator_idx in self.generator_indices:
                generator_assumption_estimates = self.generator_pool.assumptions(generator_idx)
                x = np.array(generator_assumption_estimates).reshape(1, -1)
                x_scaled = self.scalers[generator_idx].transform(x) if generator_idx in self.scalers else x
                correction_term_pred = self.models[generator_idx].predict(x_scaled)[0]
                pred = self.generator_pool.generators[generator_idx].baseline * correction_term_pred

                if pred > best_pred:
                    best_pred, best_generator_idx = pred, generator_idx
                    best_vector = x_scaled

        self.generator_to_use_idx = best_generator_idx
        if not self.train_knn:
            best_vector = best_vector.reshape(-1, 1)
            n_zeroes = 12 - best_vector.shape[0]
            best_vector = np.append(best_vector, np.zeros(n_zeroes)).reshape(1, -1)
            self.tracked_vector = best_vector[0, :]
            self.generators_used.add(self.generator_to_use_idx)

        token_allocations = generator_to_token_allocs[self.generator_to_use_idx]

        # If we're done and are supposed to train
        done = state.hare_captured() or state.stag_captured()
        if done and self.train_knn:
            # Calculate discounted rewards
            discounted_rewards, running_sum = [0] * (len(self.reward_history) - 1), 0
            for i in reversed(range(len(self.reward_history))):
                if i == 0:
                    break
                reward = self.reward_history[i] - self.reward_history[i - 1]
                running_sum = reward + 0.9 * running_sum
                discounted_rewards[i - 1] = running_sum

            # Create X and Y data
            for generator_idx, training_data in self.training_data.items():
                aat_vecs, labels = [], []

                for aat_vec, round_num in training_data:
                    assert round_num > 0
                    aat_vecs.append(aat_vec)
                    labels.append(discounted_rewards[round_num - 1])

                self.x_data[generator_idx] = self.x_data.get(generator_idx, []) + aat_vecs
                self.y_data[generator_idx] = self.y_data.get(generator_idx, []) + labels
        elif done and not self.train_knn:
            print(f'Generators used: {self.generators_used}')

        return token_allocations

    def is_hunting_hare(self) -> bool:
        return self.generator_pool.hunting_hare(self.generator_to_use_idx)
