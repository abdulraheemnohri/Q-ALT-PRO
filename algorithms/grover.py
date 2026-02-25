import numpy as np
from core.operators import apply_uniform_superposition

def grover_search(state, target_index, iterations=1):
    """
    Classical simulation of Grover's search algorithm.
    """
    # Start with uniform superposition if not already
    # apply_uniform_superposition(state) # Usually called outside

    for _ in range(iterations):
        # 1. Oracle: Flip phase of target
        state.amplitudes[target_index] *= -1

        # 2. Diffusion: 2|s><s| - I
        # Average amplitude
        avg = np.mean(state.amplitudes)
        state.amplitudes = 2 * avg - state.amplitudes

        # No need to explicitly normalize if it's a perfect reflection,
        # but good for stability.
        state.normalize()

def grover_solve(num_qubits, target_index):
    from core.state import QuantumState
    state = QuantumState(num_qubits)
    apply_uniform_superposition(state)

    # Optimal iterations approx pi/4 * sqrt(N)
    iterations = int(np.pi / 4 * np.sqrt(2**num_qubits))
    if iterations < 1: iterations = 1

    grover_search(state, target_index, iterations)
    return state
