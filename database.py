import sqlite3

DB_NAME = "mercado_analytics.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fluxo_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            tipo_evento TEXT CHECK(tipo_evento IN ('ENTRADA', 'SAIDA')),
            lotacao_momento INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS log_alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            taxa_fluxo REAL,
            caixas_recomendados INTEGER,
            status_envio TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_evento(tipo_evento: str, lotacao_momento: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO fluxo_eventos (tipo_evento, lotacao_momento) VALUES (?, ?)",
        (tipo_evento, lotacao_momento)
    )
    conn.commit()
    conn.close()

def log_alerta(taxa_fluxo: float, caixas_recomendados: int, status: str = "ENVIADO"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO log_alertas (taxa_fluxo, caixas_recomendados, status_envio) VALUES (?, ?, ?)",
        (taxa_fluxo, caixas_recomendados, status)
    )
    conn.commit()
    conn.close()