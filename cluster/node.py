import requests
from flask import Flask, request, jsonify
import numpy as np
from core.state import QuantumState
from algorithms.grover import grover_search

class WorkerNode:
    def __init__(self, port, master_url=None):
        self.app = Flask(__name__)
        self.port = port
        self.master_url = master_url
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/compute', methods=['POST'])
        def compute():
            data = request.json
            num_qubits = data.get('num_qubits')
            algorithm = data.get('algorithm')
            params = data.get('params', {})

            state = QuantumState(num_qubits)
            if 'amplitudes' in data:
                state.set_amplitudes(np.array(data['amplitudes']))

            # Execute algorithm
            if algorithm == 'grover':
                target = params.get('target')
                iterations = params.get('iterations', 1)
                grover_search(state, target, iterations)

            # Return result
            return jsonify({
                'amplitudes': state.amplitudes.tolist(),
                'status': 'completed'
            })

        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({'status': 'ok'})

    def run(self):
        self.app.run(port=self.port)

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    node = WorkerNode(port)
    node.run()
