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

    def prune(self, top_k=None, threshold=1e-6):
        """
        Top-K pruning and threshold suppression to maintain performance.
        Useful for simulating more qubits in limited memory (Termux).
        """
        # Threshold pruning
        self.amplitudes[np.abs(self.amplitudes) < threshold] = 0

        # Top-K pruning
        if top_k and top_k < self.size:
            # Get indices of top k absolute amplitudes
            indices = np.argpartition(np.abs(self.amplitudes), -top_k)[-top_k:]
            new_amplitudes = np.zeros(self.size)
            new_amplitudes[indices] = self.amplitudes[indices]
            self.amplitudes = new_amplitudes

        self.normalize()

    def get_probabilities(self):
        return np.square(self.amplitudes)

    def __repr__(self):
        return f"QuantumState(qubits={self.num_qubits}, size={self.size})"
