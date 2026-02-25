import numpy as np
from core.collapse import reinforce_collapse

def genetic_optimization(state, fitness_function, generations=50, population_size=None):
    """
    Population-based optimization using state reinforcement.
    """
    if population_size is None:
        population_size = state.size

    for gen in range(generations):
        # 1. Sample from current state to get a 'population'
        probs = state.get_probabilities()
        population = np.random.choice(state.size, size=population_size, p=probs)

        # 2. Evaluate fitness
        fitnesses = np.array([fitness_function(ind) for ind in population])

        # 3. Find best individuals
        best_idx = np.argmax(fitnesses)
        best_individual = population[best_idx]

        # 4. Reinforce best individual in the quantum state
        reinforce_collapse(state, best_individual, factor=0.2)

        # 5. Apply some 'mutation' - slight uniform noise to prevent premature convergence
        state.amplitudes += np.random.normal(0, 0.01, state.size)
        state.normalize()

    return state
