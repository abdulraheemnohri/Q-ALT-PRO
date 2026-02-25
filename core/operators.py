import numpy as np

def apply_hadamard(state, qubit_index):
    """Applies a Hadamard-like transformation to a specific qubit."""
    n = state.num_qubits
    h_matrix = np.array([[1, 1], [1, -1]]) / np.sqrt(2)

    # Reshape state to (2, 2, ..., 2)
    reshaped_state = state.amplitudes.reshape([2] * n)

    # Apply matrix to the specified axis (qubit_index)
    # We use tensordot to apply the 2x2 matrix to the specified dimension
    new_amplitudes = np.tensordot(h_matrix, reshaped_state, axes=(1, qubit_index))

    # tensordot puts the new axis at the beginning, we need to move it back
    axes = list(range(n))
    axes.pop(qubit_index)
    axes.insert(qubit_index, 0)
    # Actually tensordot(h_matrix, reshaped_state, axes=(1, qubit_index)) returns
    # a tensor where the result of the dot product (the new qubit state) is the 0-th axis.
    # We need to transpose it back to its original position.

    # Wait, a better way to do this for arbitrary axes:
    source_axes = [0] + [i + 1 for i in range(n) if i != qubit_index]
    dest_axes = list(range(n))
    # We need a permutation that moves 0 to qubit_index
    perm = list(range(1, n + 1))
    perm.insert(qubit_index, 0)

    # This is getting complicated. Let's use a simpler approach for small n.
    # Or just use np.moveaxis

    # Correct way with tensordot:
    # res = tensordot(matrix, state, axes=([1], [qubit_index]))
    # result is (2, 2, ..., 2) but with the 'new' qubit at axis 0.
    # We move axis 0 to qubit_index.

    new_amplitudes = np.tensordot(h_matrix, reshaped_state, axes=([1], [qubit_index]))
    new_amplitudes = np.moveaxis(new_amplitudes, 0, qubit_index)

    state.amplitudes = new_amplitudes.flatten()

def apply_uniform_superposition(state):
    """Sets all states to equal amplitude."""
    state.amplitudes = np.ones(state.size) / np.sqrt(state.size)

def apply_rotation(state, qubit_index, theta):
    """Applies a rotation (RY-like) to a specific qubit."""
    r_matrix = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])
    n = state.num_qubits
    reshaped_state = state.amplitudes.reshape([2] * n)
    new_amplitudes = np.tensordot(r_matrix, reshaped_state, axes=([1], [qubit_index]))
    new_amplitudes = np.moveaxis(new_amplitudes, 0, qubit_index)
    state.amplitudes = new_amplitudes.flatten()

def apply_pauli_x(state, qubit_index):
    """Applies a NOT gate."""
    x_matrix = np.array([[0, 1], [1, 0]])
    n = state.num_qubits
    reshaped_state = state.amplitudes.reshape([2] * n)
    new_amplitudes = np.tensordot(x_matrix, reshaped_state, axes=([1], [qubit_index]))
    new_amplitudes = np.moveaxis(new_amplitudes, 0, qubit_index)
    state.amplitudes = new_amplitudes.flatten()
