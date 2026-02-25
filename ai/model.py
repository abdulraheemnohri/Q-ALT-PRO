import numpy as np

class TinyNeuralNetwork:
    """
    A simple NumPy-based MLP for guiding state collapse.
    """
    def __init__(self, input_size, hidden_size, output_size):
        self.w1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.w2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))

    def forward(self, x):
        # Ensure x is 2D
        if x.ndim == 1:
            x = x.reshape(1, -1)

        self.z1 = np.dot(x, self.w1) + self.b1
        self.a1 = np.tanh(self.z1)
        self.z2 = np.dot(self.a1, self.w2) + self.b2
        # Use sigmoid for output to get reinforcement factors [0, 1]
        self.a2 = 1 / (1 + np.exp(-self.z2))
        return self.a2

    def train_step(self, x, y_target, learning_rate=0.01):
        # Forward
        y_pred = self.forward(x)

        # Backward (Simple MSE gradient)
        error = y_pred - y_target
        d_z2 = error * (y_pred * (1 - y_pred)) # Sigmoid derivative
        d_w2 = np.dot(self.a1.T, d_z2)
        d_b2 = np.sum(d_z2, axis=0, keepdims=True)

        d_a1 = np.dot(d_z2, self.w2.T)
        d_z1 = d_a1 * (1 - self.a1**2) # Tanh derivative
        d_w1 = np.dot(x.T, d_z1)
        d_b1 = np.sum(d_z1, axis=0, keepdims=True)

        # Update
        self.w1 -= learning_rate * d_w1
        self.b1 -= learning_rate * d_b1
        self.w2 -= learning_rate * d_w2
        self.b2 -= learning_rate * d_b2

        return np.mean(error**2)

class AICore:
    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        self.state_size = 2**num_qubits
        # Input: current amplitudes, Output: reinforcement mask
        self.model = TinyNeuralNetwork(self.state_size, 32, self.state_size)

    def guide_collapse(self, state):
        """
        Predict promising states and reinforce them.
        """
        reinforcement = self.model.forward(state.amplitudes)
        # Apply reinforcement
        state.amplitudes *= (1.0 + 0.1 * reinforcement.flatten())
        state.normalize()

    def learn_from_result(self, initial_amplitudes, final_outcome_idx, reward):
        """
        Train the model to prefer outcomes that lead to better rewards.
        """
        target = np.zeros((1, self.state_size))
        target[0, final_outcome_idx] = reward
        self.model.train_step(initial_amplitudes, target)
