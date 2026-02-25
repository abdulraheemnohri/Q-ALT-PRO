import requests
import concurrent.futures
import numpy as np

class ClusterMaster:
    def __init__(self, nodes=None):
        # nodes is a dict: {url: {"status": "unknown", "last_seen": timestamp}}
        self.nodes = {url: {"status": "unknown"} for url in (nodes or [])}

    def add_node(self, node_url):
        if node_url not in self.nodes:
            self.nodes[node_url] = {"status": "unknown"}

    def check_nodes(self):
        """Heartbeat check for all nodes."""
        for url in self.nodes:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    self.nodes[url]["status"] = "online"
                else:
                    self.nodes[url]["status"] = "offline"
            except:
                self.nodes[url]["status"] = "offline"
        return self.nodes

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

        online_nodes = [url for url, info in self.nodes.items() if info["status"] == "online"]
        if not online_nodes:
            # If status unknown, try all
            online_nodes = list(self.nodes.keys())

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(send_to_node, online_nodes))

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
