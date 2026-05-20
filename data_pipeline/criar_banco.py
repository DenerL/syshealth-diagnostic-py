import sqlite3
from datetime import datetime

def inicializar_banco():
    # Cria (ou conecta) o arquivo de banco de dados
    conn = sqlite3.connect('telemetria_infra.db')
    cursor = conn.cursor()
    
    # Criando a tabela com a estrutura de dados correta
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historico_maquinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_coleta DATETIME NOT NULL,
        nome_host TEXT NOT NULL,         -- Nome do PC na rede
        ip_local TEXT,
        memoria_total_mb REAL,
        armazenamento_livre_gb REAL,
        saude_bateria_percent REAL,     -- Guardamos como número para fazer médias
        status_fonte TEXT,
        latencia_google_ms REAL,
        uptime_dias INTEGER
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Banco 'telemetria_infra.db' inicializado com sucesso!")

if __name__ == "__main__":
    inicializar_banco()
