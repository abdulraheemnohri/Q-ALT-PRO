import numpy as np

def measure(state):
    """Performs a full collapse measurement."""
    probs = state.get_probabilities()
    # Handle floating point inaccuracies
    probs = probs / np.sum(probs)

    outcome = np.random.choice(state.size, p=probs)

    # Collapse the state
    new_amplitudes = np.zeros(state.size)
    new_amplitudes[outcome] = 1.0
    state.amplitudes = new_amplitudes

    return outcome

def reinforce_collapse(state, target_index, factor=0.1):
    """
    Partial collapse: Reinforce the winning amplitude and suppress others.
    This mimics amplitude amplification without full collapse.
    """
    # Increase amplitude of target_index
    state.amplitudes[target_index] *= (1.0 + factor)

    # Slightly suppress others
    mask = np.ones(state.size, dtype=bool)
    mask[target_index] = False
    state.amplitudes[mask] *= (1.0 - factor * 0.1)

    state.normalize()

def soft_collapse(state, temperature=1.0):
    """
    Applies a softmax-like sharpening to the amplitudes.
    Higher temperature (near 0) means more sharpening.
    Wait, usually temperature in softmax: exp(x/T).
    Here we can use: amplitude = amplitude ^ (1/temperature)
    """
    if temperature <= 0:
        return measure(state)

    # Sharpening
    state.amplitudes = np.power(np.abs(state.amplitudes), 1.0/temperature) * np.sign(state.amplitudes)
    state.normalize()
