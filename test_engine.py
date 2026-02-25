import numpy as np
from core.state import QuantumState
from core.operators import apply_hadamard, apply_uniform_superposition
from core.collapse import measure
from algorithms.grover import grover_search
from storage.logs import get_recent_logs
from ai.model import AICore

def test_core():
    print("Testing Core...")
    state = QuantumState(3)
    assert state.size == 8
    assert state.amplitudes[0] == 1.0

    apply_uniform_superposition(state)
    assert np.allclose(np.sum(state.get_probabilities()), 1.0)
    print("Core OK.")

def test_grover():
    print("Testing Grover...")
    state = QuantumState(4)
    apply_uniform_superposition(state)
    target = 7
    # Optimal iterations for 4 qubits (16 states) is ~3
    grover_search(state, target, iterations=3)

    probs = state.get_probabilities()
    best_idx = np.argmax(probs)
    print(f"Grover Target: {target}, Found: {best_idx}, Prob: {probs[best_idx]:.4f}")
    assert best_idx == target
    print("Grover OK.")

def test_ai():
    print("Testing AI Guidance...")
    state = QuantumState(4)
    apply_uniform_superposition(state)
    ai = AICore(4)
    ai.guide_collapse(state)
    assert np.allclose(np.sum(state.get_probabilities()), 1.0)
    print("AI OK.")

def test_storage():
    print("Testing Storage...")
    from storage.logs import log_experiment
    log_experiment("test_alg", 5, 1, 0.5, 0.1)
    logs = get_recent_logs(1)
    assert len(logs) > 0
    assert logs[0]['algorithm'] == "test_alg"
    print("Storage OK.")

if __name__ == "__main__":
    test_core()
    test_grover()
    test_ai()
    test_storage()
    print("All tests passed!")
