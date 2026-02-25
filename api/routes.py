from flask import Blueprint, request, jsonify
from core.state import QuantumState
from algorithms.grover import grover_solve
from algorithms.annealing import simulated_annealing
from storage.logs import log_experiment, get_recent_logs, DB_PATH
from storage.state_store import save_state, load_state, list_saved_states
from ai.model import AICore
import sqlite3
import csv
import io
import psutil
import time
import numpy as np
from functools import wraps
from flask import current_app
from cluster.master import ClusterMaster

api_bp = Blueprint('api', __name__)
cluster_master = ClusterMaster()

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            # Also check query param or json
            api_key = request.args.get('key') or (request.json.get('key') if request.is_json else None)

        if api_key != current_app.config.get('API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Rate limiting simple implementation
last_request_time = {}

def rate_limit(limit_seconds=1.0):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            if ip in last_request_time and now - last_request_time[ip] < limit_seconds:
                return jsonify({"error": "Too many requests"}), 429
            last_request_time[ip] = now
            return f(*args, **kwargs)
        return decorated_function
    return decorator
ai_engine = AICore(num_qubits=5) # Default, will re-init if needed

@api_bp.route('/run', methods=['POST'])
@rate_limit(0.5)
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
        # Calculate optimal iterations if not provided
        default_iters = int(np.pi / 4 * np.sqrt(state.size))
        iterations = params.get('iterations', default_iters if default_iters > 0 else 1)
        grover_search(state, target, iterations)

    elif alg_name == 'annealing':
        def target_cost(idx):
            target = params.get('target', 0)
            return abs(idx - target)
        simulated_annealing(state, target_cost,
                            initial_temp=params.get('temp', 1.0),
                            cooling_rate=params.get('cooling', 0.95),
                            iterations=params.get('iterations', 100))

    elif alg_name == 'qaoa':
        from algorithms.qaoa import qaoa_optimize
        def target_cost(idx):
            target = params.get('target', 0)
            return abs(idx - target)
        qaoa_optimize(state, target_cost,
                      p=params.get('p', 1),
                      gammas=params.get('gammas'),
                      betas=params.get('betas'))

    elif alg_name == 'genetic':
        from algorithms.genetic import genetic_optimization
        def target_fitness(idx):
            target = params.get('target', 0)
            return -abs(idx - target)
        genetic_optimization(state, target_fitness,
                             generations=params.get('generations', 50),
                             population_size=params.get('pop_size'))

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
        'version': '1.0.0',
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'nodes': cluster_master.check_nodes()
    })

@api_bp.route('/cluster/nodes/add', methods=['POST'])
def add_cluster_node():
    data = request.json
    url = data.get('url')
    if url:
        cluster_master.add_node(url)
        return jsonify({"status": "node added"})
    return jsonify({"error": "URL required"}), 400

@api_bp.route('/logs/export/<format>', methods=['GET'])
def export_logs(format):
    logs = get_recent_logs(limit=1000)
    if format == 'json':
        return jsonify(logs)
    elif format == 'csv':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=logs[0].keys() if logs else [])
        writer.writeheader()
        writer.writerows(logs)
        return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=logs.csv'}
    return jsonify({"error": "Invalid format"}), 400

@api_bp.route('/states', methods=['GET'])
def get_states():
    return jsonify(list_saved_states())

@api_bp.route('/states/save', methods=['POST'])
def api_save_state():
    data = request.json
    name = data.get('name')
    amplitudes = data.get('amplitudes')
    num_qubits = data.get('num_qubits')

    state = QuantumState(num_qubits)
    state.set_amplitudes(amplitudes)
    save_state(name, state)
    return jsonify({"status": "saved"})

@api_bp.route('/states/load/<name>', methods=['GET'])
def api_load_state(name):
    state = load_state(name)
    if state:
        return jsonify({
            "num_qubits": state.num_qubits,
            "amplitudes": state.amplitudes.tolist()
        })
    return jsonify({"error": "Not found"}), 404
