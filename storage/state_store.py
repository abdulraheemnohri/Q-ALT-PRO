import sqlite3
import numpy as np
import datetime
from storage.logs import DB_PATH

def save_state(name, state):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Serialize amplitudes to bytes
    amplitudes_bytes = state.amplitudes.tobytes()

    cursor.execute('''
        INSERT OR REPLACE INTO states (name, num_qubits, amplitudes, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (name, state.num_qubits, amplitudes_bytes, datetime.datetime.now()))
    conn.commit()
    conn.close()

def load_state(name):
    from core.state import QuantumState
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT num_qubits, amplitudes FROM states WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        num_qubits, amplitudes_bytes = row
        state = QuantumState(num_qubits)
        state.amplitudes = np.frombuffer(amplitudes_bytes, dtype=np.float64)
        return state
    return None

def list_saved_states():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT name, num_qubits, timestamp FROM states ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows
