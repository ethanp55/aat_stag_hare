import numpy as np
import os
import pickle
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler

# Read in the training data
generator_to_alignment_vectors, generator_to_correction_terms = {}, {}
training_data_folder = '../aat/training_data/'
enhanced = True
adjustment = '_enh' if enhanced else ''

for file in os.listdir(training_data_folder):
    if (enhanced and '_enh' not in file) or (not enhanced and '_enh' in file) or 'sin_c' in file:
        continue

    generator_idx = file.split('_')[1]
    data = np.genfromtxt(f'{training_data_folder}{file}', delimiter=',', skip_header=0)
    if data.shape[0] == 0:
        continue
    is_alignment_vectors = 'vectors' in file
    map_to_add_to = generator_to_alignment_vectors if is_alignment_vectors else generator_to_correction_terms
    map_to_add_to[generator_idx] = data

# Make sure the training data was read in properly
for generator_idx, vectors in generator_to_alignment_vectors.items():
    correction_terms = generator_to_correction_terms[generator_idx]

    assert len(vectors) == len(correction_terms)

# Train KNN models for each generator
for generator_idx, x in generator_to_alignment_vectors.items():
    y = generator_to_correction_terms[generator_idx]

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

    with open(f'../aat/knn_models/generator_{generator_idx}_knn{adjustment}.pickle', 'wb') as f:
        pickle.dump(knn, f)

    with open(f'../aat/knn_models/generator_{generator_idx}_scaler{adjustment}.pickle', 'wb') as f:
        pickle.dump(scaler, f)

    # Print metrics and best number of neighbors
    print(f'Best MSE: {-cv_scores[np.argmax(cv_scores)]}')
    print(f'Best R-squared: {r2_score(y, knn.predict(x_scaled))}')
    print(f'N neighbors: {n_neighbors}\n')
