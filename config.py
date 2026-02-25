import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'qalt-pro-secret-key')
    API_KEY = os.environ.get('API_KEY', 'admin-key-123')
    DEBUG = True
    DATABASE = 'qalt_pro.db'
    DEFAULT_QUBITS = 5
    MAX_QUBITS = 12
