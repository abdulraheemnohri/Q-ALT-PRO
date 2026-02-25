import numpy as np

class QuantumState:
    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        self.size = 2**num_qubits
        # Initialize to |0...0> state
        self.amplitudes = np.zeros(self.size, dtype=np.float64)
        self.amplitudes[0] = 1.0

    def set_amplitudes(self, amplitudes):
        if len(amplitudes) != self.size:
            raise ValueError(f"Expected amplitude vector of size {self.size}")
        self.amplitudes = np.array(amplitudes, dtype=np.float64)
        self.normalize()

    def normalize(self):
        norm = np.linalg.norm(self.amplitudes)
        if norm > 0:
            self.amplitudes /= norm
        else:
            self.amplitudes[0] = 1.0

    def get_probabilities(self):
        return np.square(self.amplitudes)

    def __repr__(self):
        return f"QuantumState(qubits={self.num_qubits}, size={self.size})"
