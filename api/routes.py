from flask import Blueprint, request, jsonify
from core.state import QuantumState
from algorithms.grover import grover_solve
from algorithms.annealing import simulated_annealing
from storage.logs import log_experiment, get_recent_logs
from ai.model import AICore
import time

api_bp = Blueprint('api', __name__)
ai_engine = AICore(num_qubits=5) # Default, will re-init if needed

@api_bp.route('/run', methods=['POST'])
def run_algorithm():
    data = request.json
    alg_name = data.get('algorithm')
    num_qubits = data.get('num_qubits', 5)
    params = data.get('params', {})
    use_ai = data.get('use_ai', False)

    start_time = time.time()
    state = QuantumState(num_qubits)

    if alg_name == 'grover':
        target = params.get('target', 0)
        from core.operators import apply_uniform_superposition
        apply_uniform_superposition(state)
        from algorithms.grover import grover_search
        iterations = params.get('iterations', 1)
        grover_search(state, target, iterations)

    elif alg_name == 'annealing':
        def dummy_cost(idx):
            # Example: minimize distance to target
            target = params.get('target', 0)
            return abs(idx - target)
        simulated_annealing(state, dummy_cost)

    elif alg_name == 'qaoa':
        from algorithms.qaoa import qaoa_optimize
        def dummy_cost(idx):
            target = params.get('target', 0)
            return abs(idx - target)
        qaoa_optimize(state, dummy_cost, p=params.get('p', 1))

    elif alg_name == 'genetic':
        from algorithms.genetic import genetic_optimization
        def dummy_fitness(idx):
            target = params.get('target', 0)
            return -abs(idx - target)
        genetic_optimization(state, dummy_fitness)

    if use_ai:
        global ai_engine
        if ai_engine.num_qubits != num_qubits:
            ai_engine = AICore(num_qubits)
        ai_engine.guide_collapse(state)

    # Final measurement
    from core.collapse import measure
    result_idx = measure(state)
    duration = time.time() - start_time

    # Calculate "energy" (dummy for now)
    energy = abs(result_idx - params.get('target', 0))

    log_experiment(alg_name, num_qubits, int(result_idx), float(energy), duration)

    return jsonify({
        'result_index': int(result_idx),
        'duration': duration,
        'energy': float(energy),
        'probabilities': state.get_probabilities().tolist()
    })

@api_bp.route('/logs', methods=['GET'])
def get_logs():
    limit = request.args.get('limit', 10, type=int)
    return jsonify(get_recent_logs(limit))

@api_bp.route('/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'engine': 'Q-ALT PRO',
        'version': '1.0.0'
    })
