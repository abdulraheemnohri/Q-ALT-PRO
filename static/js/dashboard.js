document.addEventListener('DOMContentLoaded', () => {
    const qubitSlider = document.getElementById('qubitSlider');
    const qubitValue = document.getElementById('qubitValue');
    const runBtn = document.getElementById('runBtn');
    const probChartCtx = document.getElementById('probChart').getContext('2d');

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

    qubitSlider.addEventListener('input', (e) => {
        qubitValue.textContent = e.target.value;
    });

    runBtn.addEventListener('click', async () => {
        runBtn.disabled = true;
        runBtn.textContent = 'RUNNING...';

        const payload = {
            algorithm: document.getElementById('algoSelect').value,
            num_qubits: parseInt(qubitSlider.value),
            params: {
                target: parseInt(document.getElementById('targetIndex').value),
                iterations: 2
            },
            use_ai: document.getElementById('useAI').checked
        };

        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();

            updateDashboard(result);
            fetchLogs();
        } catch (error) {
            console.error('Error running engine:', error);
        } finally {
            runBtn.disabled = false;
            runBtn.textContent = 'RUN ENGINE';
        }
    });

    function updateDashboard(result) {
        document.getElementById('statusInfo').innerHTML = `
            <p>Result Index: <span class="text-cyan-400 font-bold">${result.result_index}</span></p>
            <p>Duration: <span class="text-cyan-400">${result.duration.toFixed(4)}s</span></p>
            <p>Energy: <span class="text-cyan-400">${result.energy.toFixed(2)}</span></p>
        `;

        const probs = result.probabilities;
        probChart.data.labels = probs.map((_, i) => i);
        probChart.data.datasets[0].data = probs;
        probChart.update();
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

    fetchLogs();
});
