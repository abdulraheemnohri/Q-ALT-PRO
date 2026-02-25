import requests
import concurrent.futures
import numpy as np

class ClusterMaster:
    def __init__(self, nodes=None):
        self.nodes = nodes or []

    def add_node(self, node_url):
        if node_url not in self.nodes:
            self.nodes.append(node_url)

    def distribute_task(self, num_qubits, algorithm, params):
        """
        Distribute a task across all registered nodes and aggregate results.
        """
        if not self.nodes:
            raise Exception("No worker nodes available")

        def send_to_node(node_url):
            try:
                response = requests.post(f"{node_url}/compute", json={
                    'num_qubits': num_qubits,
                    'algorithm': algorithm,
                    'params': params
                }, timeout=10)
                return response.json()
            except Exception as e:
                return {'error': str(e)}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(send_to_node, self.nodes))

        return results

    def aggregate_amplitudes(self, results):
        """
        Aggregates amplitudes from multiple nodes (e.g., by averaging or summing).
        """
        valid_results = [r['amplitudes'] for r in results if 'amplitudes' in r]
        if not valid_results:
            return None

        # Simple averaging for demonstration
        mean_amplitudes = np.mean(valid_results, axis=0)
        return mean_amplitudes
