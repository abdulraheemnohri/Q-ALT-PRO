document.addEventListener('DOMContentLoaded', () => {
    const qubitSlider = document.getElementById('qubitSlider');
    const qubitValue = document.getElementById('qubitValue');
    const runBtn = document.getElementById('runBtn');
    const probChartCtx = document.getElementById('probChart').getContext('2d');
    const energyChartCtx = document.getElementById('energyChart').getContext('2d');

    let probChart = new Chart(probChartCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Probability',
                data: [],
                backgroundColor: 'rgba(34, 211, 238, 0.6)',
                borderColor: 'rgba(34, 211, 238, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 1, grid: { color: '#334155' } },
                x: { grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });

    let energyChart = new Chart(energyChartCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Energy',
                data: [],
                borderColor: 'rgba(239, 68, 68, 1)',
                backgroundColor: 'rgba(239, 68, 68, 0.2)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: '#334155' } },
                x: { grid: { color: '#334155' } }
            },
            plugins: { legend: { display: false } }
        }
    });

    qubitSlider.addEventListener('input', (e) => {
        qubitValue.textContent = e.target.value;
    });

    const algoSelect = document.getElementById('algoSelect');
    algoSelect.addEventListener('change', (e) => {
        document.querySelectorAll('.algo-param-group').forEach(el => el.classList.add('hidden'));
        const target = document.getElementById(`params_${e.target.value}`);
        if (target) target.classList.remove('hidden');
    });

    function logToConsole(msg) {
        const console = document.getElementById('engineConsole');
        const p = document.createElement('p');
        p.textContent = `> [${new Date().toLocaleTimeString()}] ${msg}`;
        console.appendChild(p);
        console.scrollTop = console.scrollHeight;
    }

    runBtn.addEventListener('click', async () => {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.remove('hidden');
        runBtn.classList.add('pulse-on-run');
        runBtn.disabled = true;
        runBtn.textContent = 'RUNNING...';

        const algo = algoSelect.value;
        logToConsole(`Launching ${algo.toUpperCase()}...`);
        const params = {
            target: parseInt(document.getElementById('targetIndex').value)
        };

        if (algo === 'grover') {
            const iters = parseInt(document.getElementById('grover_iters').value);
            if (iters > 0) params.iterations = iters;
        } else if (algo === 'annealing') {
            params.temp = parseFloat(document.getElementById('anneal_temp').value);
            params.cooling = parseFloat(document.getElementById('anneal_cooling').value);
        } else if (algo === 'qaoa') {
            params.p = parseInt(document.getElementById('qaoa_p').value);
        } else if (algo === 'genetic') {
            params.generations = parseInt(document.getElementById('genetic_gens').value);
        }

        const payload = {
            algorithm: algo,
            num_qubits: parseInt(qubitSlider.value),
            params: params,
            use_ai: document.getElementById('useAI').checked
        };

        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();

            updateDashboard(result, parseInt(qubitSlider.value));
            fetchLogs();
        } catch (error) {
            console.error('Error running engine:', error);
        } finally {
            overlay.classList.add('hidden');
            runBtn.classList.remove('pulse-on-run');
            runBtn.disabled = false;
            runBtn.textContent = 'RUN ENGINE';
        }
    });

    let energyHistory = [];

    function updateDashboard(result, numQubits) {
        energyHistory.push(result.energy);
        if (energyHistory.length > 20) energyHistory.shift();

        document.getElementById('resIndex').textContent = result.result_index;
        document.getElementById('resBits').textContent = result.result_index.toString(2).padStart(numQubits, '0');
        logToConsole(`Run complete. Result: |${result.result_index}> (${result.duration.toFixed(4)}s)`);

        const probs = result.probabilities;
        probChart.data.labels = probs.map((_, i) => i);
        probChart.data.datasets[0].data = probs;
        probChart.update();

        energyChart.data.labels = energyHistory.map((_, i) => i);
        energyChart.data.datasets[0].data = energyHistory;
        energyChart.update();
    }

    async function fetchLogs() {
        try {
            const response = await fetch('/api/logs?limit=5');
            const logs = await response.json();
            const logList = document.getElementById('logList');
            logList.innerHTML = logs.map(log => `
                <div class="flex justify-between border-b border-slate-700 py-1">
                    <span>${log.algorithm} (q=${log.num_qubits})</span>
                    <span class="text-cyan-400">#${log.result_index}</span>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error fetching logs:', error);
        }
    }

    async function fetchStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            document.getElementById('cpuUsage').textContent = data.cpu_usage + '%';
            document.getElementById('memUsage').textContent = data.memory_usage + '%';

            // Update cluster node list
            const clusterNodeList = document.getElementById('clusterNodeList');
            const nodes = data.nodes || {};
            clusterNodeList.innerHTML = Object.entries(nodes).map(([url, info]) => `
                <div class="flex justify-between items-center bg-slate-700/50 p-2 rounded border border-slate-600">
                    <span class="text-xs truncate max-w-[150px]">${url}</span>
                    <span class="text-[10px] px-2 py-0.5 rounded ${info.status === 'online' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">
                        ${info.status.toUpperCase()}
                    </span>
                </div>
            `).join('') || '<p class="text-xs text-slate-500 italic text-center">No nodes connected</p>';

        } catch (error) {
            console.error('Error fetching status:', error);
        }
    }

    async function fetchStates() {
        try {
            const response = await fetch('/api/states');
            const states = await response.json();
            const stateList = document.getElementById('stateList');
            stateList.innerHTML = states.map(state => `
                <div class="flex justify-between border-b border-slate-700 py-1">
                    <span>${state[0]} (q=${state[1]})</span>
                    <button onclick="loadState('${state[0]}')" class="text-cyan-400 hover:text-cyan-300">Load</button>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error fetching states:', error);
        }
    }

    window.addNode = async () => {
        const url = document.getElementById('nodeUrl').value;
        if (!url) return;
        try {
            const response = await fetch('/api/cluster/nodes/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            if (response.ok) {
                document.getElementById('nodeUrl').value = '';
                fetchStatus();
            }
        } catch (error) {
            console.error('Error adding node:', error);
        }
    };

    window.exportLogs = async (format) => {
        window.location.href = `/api/logs/export/${format}`;
    };

    window.loadState = async (name) => {
        try {
            const response = await fetch(`/api/states/load/${name}`);
            const data = await response.json();
            qubitSlider.value = data.num_qubits;
            qubitValue.textContent = data.num_qubits;
            // Update chart with loaded amplitudes
            const probs = data.amplitudes.map(a => a * a);
            probChart.data.labels = probs.map((_, i) => i);
            probChart.data.datasets[0].data = probs;
            probChart.update();
            alert(`Loaded state: ${name}`);
        } catch (error) {
            alert('Error loading state');
        }
    };

    setInterval(fetchStatus, 3000);
    fetchLogs();
    fetchStates();
    fetchStatus();
});
