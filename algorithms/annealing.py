import numpy as np

def simulated_annealing(state, cost_function, initial_temp=1.0, cooling_rate=0.95, iterations=100):
    """
    Simulated Annealing over the probabilistic state.
    """
    temp = initial_temp

    # Precompute costs
    costs = np.array([cost_function(idx) for idx in range(state.size)])

    for _ in range(iterations):
        # Boltzmann weighting
        target_probs = np.exp(-costs / (temp + 1e-9))
        target_probs /= np.sum(target_probs)

        # Move amplitudes towards target_probs
        # state.amplitudes^2 should match target_probs
        target_amplitudes = np.sqrt(target_probs)

        # Soft update
        state.amplitudes = 0.8 * state.amplitudes + 0.2 * target_amplitudes
        state.normalize()

        temp *= cooling_rate

    return state
