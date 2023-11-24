import numpy as np

from model_merging import hdf5_util
from model_merging import fisher


def generate_fisher_distributions(fisher_matrices):
    """
    Generates a distribution of Fisher information over the layers of the model.
    NOTE: This function also calculates the total and average Fisher information for each layer.

    Parameters:
    - fisher_matrices: List of Fisher information matrices for each model.

    Returns:
    - list: List of numpy arrays containing the Fisher information distributions for each layer.
    """
    fisher_dists = []
    for fisher_mat in fisher_matrices:
        n = len(fisher_mat) // 16
        results = np.zeros((n, 3))

        for i in range(n):
            layer_matrices = fisher_mat[i * 16:(i + 1) * 16]  # Get the matrices for each layer
            layer_sum = sum(np.sum(matrix.numpy()) for matrix in layer_matrices)
            layer_avg = layer_sum / sum(matrix.numpy().size for matrix in layer_matrices)

            results[i, 0] = layer_avg
            results[i, 1] = layer_sum

        # Calculate the total sum
        total_sum = np.sum(results[:, 1])

        # Calculate the proportion of the total for each layer
        results[:, 2] = results[:, 1] / total_sum
        fisher_dists.append(results[:, 2])

    return fisher_dists


def sample_from_vector(vector, weight_vec, center, alpha_blend, spread=1.0):
    """
    Selects a single element from a given vector based on a combination of location-based
    and provided weights.

    Parameters:
    - vector: List of integers to sample from.
    - weight_vec: Vector of weights corresponding to each element in 'vector'.
    - center: Center index for Gaussian-like location weighting.
    - alpha_blend: Blend factor between location-based weights and 'weight_vec'.
                    0 = pure 'weight_vec', 1 = pure location-based.
    - spread: Spread of the Gaussian-like weighting (default is 1.0).

    Returns:
    - int: A randomly selected element from the input vector.
    """
    if len(vector) == 0:
        raise ValueError("Input vector is empty.")

    if len(vector) == 1:
        return vector[0]

    loc_probabilities = np.exp(-0.5 * ((np.arange(len(vector)) - center) / spread) ** 2)
    loc_probabilities /= loc_probabilities.sum()  # Normalize to make it a probability distribution
    return np.random.choice(vector, p=alpha_blend * loc_probabilities + (1 - alpha_blend) * weight_vec)


def generate_weighted_vector(input_vectors, output_length=None, weight_vectors=None,
                             alpha_blend=0.5, beta_choice=0.5, loc_spread=1.0):
    """
    Generates a new vector of integers by selectively sampling from two input vectors.

    Parameters:
    - input_vector1, input_vector2: Input vectors of integers.
    - output_length: Desired length of the output vector. Defaults to the length of input_vector1.
    - weight1, weight2: Weight vectors for input_vector1 and input_vector2. Default to uniform weights.
    - alpha_blend: Blend factor for weighting schemes in sampling.
                    0 = pure weight_vec, 1 = pure location-based.
    - beta_choice: Blend factor for final choice between two vectors.
                    0 = pure input_vector1, 1 = pure input_vector2.

    Returns:
    - numpy.array: The resulting weighted vector.
    """
    if len(input_vectors) != 2:
        raise ValueError("Must provide exactly two input vectors.")

    input_vector1 = input_vectors[0]
    input_vector2 = input_vectors[1]

    if len(input_vector1) == 0 or len(input_vector2) == 0:
        raise ValueError("Input vectors must not be empty.")

    n_1, n_2 = len(input_vector1), len(input_vector2)
    output_length = output_length if output_length is not None else n_1
    weight1 = weight_vectors[0] if weight_vectors is not None else np.ones(n_1) / n_1
    weight2 = weight_vectors[1] if weight_vectors is not None else np.ones(n_2) / n_2

    rng = np.random.default_rng()

    result = []
    for i in range(output_length):
        index1 = int((n_1 - 1) * (i / output_length))
        index2 = int((n_2 - 1) * (i / output_length))

        value1 = sample_from_vector(input_vector1, weight1, index1, alpha_blend, loc_spread)
        value2 = sample_from_vector(input_vector2, weight2, index2, alpha_blend, loc_spread)

        result.append(rng.choice(a=[value1, value2], p=[beta_choice, 1 - beta_choice]))

    return np.array(result)


def generate_layer_config(fishers, sampling_config=None):
    """
    Generates a layer configuration for the new model.
    1. Load fisher matrices for each model.
    2. Generate a weight vector for each layer from fisher info.
    3. Generate a new layer config by sampling from the weight vectors.
    4. Return the new layer config.

    Returns:
    - dict: A dictionary containing the model configuration.
    """

    fisher_dists = generate_fisher_distributions(fishers)

    layers = generate_weighted_vector(fisher_dists, output_length=12)




