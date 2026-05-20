import sqlite3

def ler_historico():
    try:
        conn = sqlite3.connect('telemetria_infra.db')
        cursor = conn.cursor()
        
        # Buscamos todos os registros salvos, ordenados pelo mais recente
        cursor.execute("SELECT data_coleta, nome_host, memoria_total_mb, armazenamento_livre_gb, latencia_google_ms FROM historico_maquinas ORDER BY data_coleta DESC")
        linhas = cursor.fetchall()
        
        print("\n" + "="*70)
        print(f"{'DATA/HORA COLETA':<20} | {'MÁQUINA':<12} | {'RAM (MB)':<10} | {'DISCO LIVRE':<12} | {'PINGS (ms)'}")
        print("="*70)
        
        for linha in linhas:
            print(f"{linha[0]:<20} | {linha[1]:<12} | {linha[2]:<10.2f} | {linha[3]:<9} GB | {linha[4]:.1f} ms")
            
        print("="*70 + "\n")
        
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao ler dados: {e}")

if __name__ == "__main__":
    ler_historico()
