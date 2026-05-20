import os
import sys
import time
import ctypes
import re
import subprocess
import socket
import sqlite3
from datetime import datetime
import psutil

def run_ps(cmd):
    """Executa comando PowerShell de forma silenciosa e captura o retorno."""
    try:
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", cmd], 
                               capture_output=True, text=True, errors='replace', timeout=15)
        return result.stdout.strip()
    except:
        return ""

def coletar_telemetria():
    """Coleta todos os dados do sistema e retorna um dicionário limpo."""
    dados = {}
    
    # 1. Timestamp e Hostname
    dados['data_coleta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dados['nome_host'] = socket.gethostname()
    
    # 2. IP Local
    ip_cmd = "Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Ethernet*' | Where-Object {$_.IPAddress -ne '127.0.0.1'} | Select-Object -First 1 -ExpandProperty IPAddress"
    ip_res = run_ps(ip_cmd)
    dados['ip_local'] = ip_res if ip_res else "127.0.0.1"
    
    # 3. Memória RAM Total (em MB)
    dados['memoria_total_mb'] = round(psutil.virtual_memory().total / (1024**2), 2)
    
    # 4. Armazenamento Livre (C: em GB)
    try:
        dados['armazenamento_livre_gb'] = psutil.disk_usage('C:').free // (1024**3)
    except:
        dados['armazenamento_livre_gb'] = 0.0

    # 5. Saúde da Bateria (Lógica Universal)
    bat_health = None
    try:
        cmd_bat = "Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue | ForEach-Object { [math]::Round(($_.FullChargeCapacity / $_.DesignCapacity) * 100, 1) }"
        res_bat = run_ps(cmd_bat)
        match = re.search(r"(\d+[\.,]?\d*)", res_bat)
        if match:
            bat_health = min(float(match.group(1).replace(',', '.')), 100.0)
    except:
        pass
    dados['saude_bateria_percent'] = bat_health # Pode salvar como None (NULL no SQL) se for Desktop

    # 6. Status da Fonte
    psu_status = "DESCONHECIDO"
    try:
        cmd_status = "(Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue).BatteryStatus"
        res_status = run_ps(cmd_status)
        if "2" in res_status:
            psu_status = "CONECTADO"
        elif "1" in res_status:
            psu_status = "NA BATERIA"
        else:
            cmd_psu = "(Get-CimInstance Win32_PowerSupply -ErrorAction SilentlyContinue).Status"
            res_psu = run_ps(cmd_psu)
            if res_psu: psu_status = res_psu.upper()
    except:
        pass
    dados['status_fonte'] = psu_status

    # 7. Latência Média (Google)
    dados['latencia_google_ms'] = 999.0 # Default caso falhe
    res = subprocess.run(["ping", "-n", "2", "8.8.8.8"], capture_output=True, text=True, errors='replace')
    if res.returncode == 0:
        match = re.search(r"(?:tempo|time)\s*=\s*(\d+)\s*ms", res.stdout, re.IGNORECASE)
        if match:
            dados['latencia_google_ms'] = float(match.group(1))

    # 8. Uptime (Dias)
    uptime_dias = 0
    try:
        uptime_cmd = "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime"
        # Simplificado para pegar os dias aproximados via PowerShell puro se necessário, 
        # ou pegamos direto do psutil que é mais rápido:
        uptime_dias = int((time.time() - psutil.boot_time()) // 86400)
    except:
        pass
    dados['uptime_dias'] = uptime_dias

    return dados

def salvar_no_banco(dados):
    """Conecta no banco SQLite e insere o dicionário de dados."""
    try:
        conn = sqlite3.connect('telemetria_infra.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO historico_maquinas (
            data_coleta, nome_host, ip_local, memoria_total_mb, 
            armazenamento_livre_gb, saude_bateria_percent, status_fonte, 
            latencia_google_ms, uptime_dias
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados['data_coleta'], dados['nome_host'], dados['ip_local'], dados['memoria_total_mb'],
            dados['armazenamento_livre_gb'], dados['saude_bateria_percent'], dados['status_fonte'],
            dados['latencia_google_ms'], dados['uptime_dias']
        ))
        
        conn.commit()
        conn.close()
        print(f"📥 [DATA INGESTION] Dados da máquina '{dados['nome_host']}' salvos com sucesso às {dados['data_coleta']}!")
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando coleta de telemetria...")
    dados_coletados = coletar_telemetria()
    salvar_no_banco(dados_coletados)
