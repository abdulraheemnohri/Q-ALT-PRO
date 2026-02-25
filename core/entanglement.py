import numpy as np

class CorrelationEngine:
    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        # Correlation matrix C[i][j]
        self.matrix = np.zeros((num_qubits, num_qubits))

    def set_correlation(self, i, j, value):
        self.matrix[i][j] = value
        self.matrix[j][i] = value

    def apply_correlations(self, state):
        """
        Adjust amplitudes based on correlations.
        If C[i][j] is high, then states where qubit i and j are the same
        (or different, depending on sign) are reinforced.
        """
        for i in range(self.num_qubits):
            for j in range(i + 1, self.num_qubits):
                corr = self.matrix[i][j]
                if corr == 0:
                    continue

                # Reinforce or suppress based on corr
                # For each state index, check bits i and j
                for idx in range(state.size):
                    bit_i = (idx >> i) & 1
                    bit_j = (idx >> j) & 1

                    if bit_i == bit_j:
                        # Reinforce if corr > 0, suppress if corr < 0
                        state.amplitudes[idx] *= (1.0 + corr)
                    else:
                        # Suppress if corr > 0, reinforce if corr < 0
                        state.amplitudes[idx] *= (1.0 - corr)

        state.normalize()
