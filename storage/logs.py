import sqlite3
import json
import numpy as np
import datetime

DB_PATH = "qalt_pro.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Table for logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            algorithm TEXT,
            num_qubits INTEGER,
            result_index INTEGER,
            energy REAL,
            duration REAL,
            metadata TEXT
        )
    ''')
    # Table for states
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS states (
            name TEXT PRIMARY KEY,
            num_qubits INTEGER,
            amplitudes BLOB,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def log_experiment(algorithm, num_qubits, result_index, energy, duration, metadata=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (timestamp, algorithm, num_qubits, result_index, energy, duration, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.datetime.now(), algorithm, num_qubits, result_index, energy, duration, json.dumps(metadata)))
    conn.commit()
    conn.close()

def get_recent_logs(limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
