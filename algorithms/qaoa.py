import numpy as np
from core.operators import apply_rotation, apply_uniform_superposition

def qaoa_optimize(state, cost_function, p=1, gammas=None, betas=None):
    """
    QAOA-inspired optimization.
    cost_function: maps index to a real value (energy).
    """
    if gammas is None: gammas = [0.1] * p
    if betas is None: betas = [0.1] * p

    # Start with uniform superposition
    apply_uniform_superposition(state)

    for i in range(p):
        gamma = gammas[i]
        beta = betas[i]

        # 1. Cost layer: exp(-i * gamma * C)
        # We use a phase shift proportional to cost
        # amplitudes[j] *= exp(-1j * gamma * cost(j))
        # Since we use real amplitudes, we might use a rotation or a real-valued weighting
        # For a truly quantum-inspired classical engine, we can use:
        costs = np.array([cost_function(idx) for idx in range(state.size)])
        # Normalize costs for stability
        costs = (costs - np.min(costs)) / (np.max(costs) - np.min(costs) + 1e-9)

        # Applying complex phase would require complex amplitudes.
        # Let's switch to complex amplitudes in state.py if we want true QAOA.
        # BUT the prompt said real amplitudes.
        # "Quantum-Inspired" classical can use weighting:
        state.amplitudes *= np.exp(-gamma * costs)
        state.normalize()

        # 2. Mixer layer: exp(-i * beta * B)
        # In QAOA this is a rotation on each qubit.
        for q in range(state.num_qubits):
            apply_rotation(state, q, beta)

    return state

def solve_maxcut_sample(state, adjacency_matrix):
    # Example cost function for Max-Cut
    def cost_func(idx):
        # Convert idx to bitstring
        bits = [(idx >> i) & 1 for i in range(state.num_qubits)]
        cut = 0
        for i in range(len(bits)):
            for j in range(i + 1, len(bits)):
                if bits[i] != bits[j]:
                    cut += adjacency_matrix[i][j]
        return -cut # We want to minimize, so return negative cut

    return qaoa_optimize(state, cost_func)
