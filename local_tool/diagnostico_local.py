import os
import sys
import time
import ctypes
import re
import subprocess
import traceback
import psutil

# Constantes de Cores ANSI
C_RESET = "0"
C_RED = "31"
C_GREEN = "32"
C_YELLOW = "33"
C_CYAN = "36"
C_BOLD_CYAN = "1;36"

# Aumenta o limite de recursão para evitar erros comuns no PyInstaller
sys.setrecursionlimit(5000)

def run_ps(cmd):
    """
    Executa comando PowerShell e retorna o resultado.
    Inclui tratamento de erros básico.
    """
    try:
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", cmd], capture_output=True, text=True, errors='replace', timeout=15)
    except subprocess.TimeoutExpired:
        return "Erro: Tempo limite excedido"
    if result.returncode != 0:
        print_warning(f"Erro ao executar PowerShell: {cmd}\n{result.stderr.strip()}")
    return result.stdout.strip()

def print_colored(text, color_code):
    """Retorna texto formatado com cor ANSI."""
    return f"\033[{color_code}m{text}\033[0m"

def print_warning(text):
    """Exibe um aviso em amarelo."""
    print(print_colored(f"[!] {text}", C_YELLOW))

def progress_bar(percent, width=20):
    """Cria uma barra de progresso visual colorida."""
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    color = C_GREEN if percent < 70 else C_YELLOW if percent < 90 else C_RED
    return print_colored(f"[{bar}] {percent}%", color)

def log_header(titulo):
    """Imprime um cabeçalho formatado."""
    header = f" {titulo} "
    print(f"\n" + print_colored(f"{header:=^60}", C_BOLD_CYAN))

def diagnosticar_processos():
    log_header("RANKING DE CONSUMO DE MEMÓRIA (RAM)")
    # Aumentamos para os 10 primeiros e focamos em RAM
    
    mem_total = psutil.virtual_memory().total / (1024**2) # Calculado uma vez fora do loop
    processos = sorted(psutil.process_iter(['name', 'memory_percent', 'cpu_percent']), 
                       key=lambda x: x.info['memory_percent'], reverse=True)[:10]
    
    print(f"{'Nome do Processo':<25} | {'Uso de RAM':<15} | {'CPU %':<8}")
    print("-" * 55)
    for p in processos:
        # Converte porcentagem em MB aproximado
        mem_usada = (p.info['memory_percent'] / 100) * mem_total
        
        line = f"{p.info['name'][:24]:<25} | {mem_usada:>7.2f} MB     | {p.info['cpu_percent']:>6.1f}%"
        color = C_RED if mem_usada > 800 or p.info['cpu_percent'] > 70 else C_RESET
        print(print_colored(line, color))
        
def verificar_usuarios_locais():
    log_header("USUÁRIOS E PERMISSÕES")
    # Tentamos listar o grupo em Inglês e Português para garantir compatibilidade
    cmd = """
    $group = Get-LocalGroup | Where-Object { $_.SID -eq "S-1-5-32-544" };
    if ($group) { Get-LocalGroupMember -Group $group.Name | Select-Object -ExpandProperty Name }
    """
    # O shell=True as vezes ajuda em comandos de rede/locais no Windows
    output = run_ps(cmd)
    
    print("Administradores Locais Encontrados:")
    if output:
        print(print_colored(output, C_CYAN))
    else:
        print_warning("Não foi possível listar os membros. Verifique se possui privilégios de Administrador.")

def status_seguranca():
    log_header("SEGURANÇA DO ENDPOINT")
    cmd = "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | Select-Object displayName, productState"
    output = run_ps(cmd)
    
    if output:
        print("Antivírus Detectados:")
        print(print_colored(output, C_CYAN))
    else:
        print(print_colored("⚠️ Nenhum Antivírus detectado via WMI!", C_RED))

def exibir_saude_discos():
    log_header("SAÚDE DOS DISPOSITIVOS DE ARMAZENAMENTO")
    """Analisa espaço e integridade física dos discos."""
    disco = psutil.disk_usage('C:')
    print(f"Armazenamento (C:): {progress_bar(disco.percent)} ({disco.free // (1024**3)} GB livres)")

    disk_life_cmd = 'Get-PhysicalDisk | ForEach-Object { $r = $_ | Get-StorageReliabilityCounter; $life = if($r.Wear -ne $null){100-$r.Wear}else{"N/A"}; "$($_.FriendlyName);$($_.HealthStatus);$($_.OperationalStatus);$($_.MediaType);$($_.BusType);$life" }'
    disk_life_out = run_ps(disk_life_cmd)
    if disk_life_out:
        print("\nUnidades Físicas:")
        for line in disk_life_out.splitlines():
            parts = line.split(';')
            if len(parts) == 6:
                name, health, status, media, bus, life = parts
                vida = f"{life}%" if life != "N/A" else ("100% (Saudável)" if health == "OK" else "Verificar")
                cor = C_GREEN if health == "OK" else C_YELLOW if health == "Warning" else C_CYAN
                print(f"  - {name}:")
                print(print_colored(f"    Tipo: {media} ({bus}) | Status: {status} | Vida: {vida} | Saúde: {health}", cor))
            else:
                print_warning(f"Erro ao analisar linha de disco: '{line}'")

def exibir_saude_energia():
    log_header("SAÚDE DA BATERIA E FONTE DE ALIMENTAÇÃO")
    """Analisa bateria e fonte de alimentação."""
    bat_health = "N/A"
    try:
        cmd_bat = "Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue | ForEach-Object { [math]::Round(($_.FullChargeCapacity / $_.DesignCapacity) * 100, 1) }"
        res_bat = subprocess.run(["powershell", "-Command", cmd_bat], capture_output=True, text=True, timeout=5)
        
        if res_bat.stdout.strip():
            match = re.search(r"(\d+[\.,]?\d*)", res_bat.stdout)
            if match:
                valor = float(match.group(1).replace(',', '.'))
                bat_health = min(valor, 100.0)
    except:
        pass

    if isinstance(bat_health, float):
        print(f"Saúde da Bateria:     {progress_bar(bat_health)}")
    else:
        print("Saúde da Bateria:     N/A (Desktop ou Sem Bateria)")

    psu_status = "N/A"
    try:
        cmd_psu = "(Get-CimInstance Win32_PowerSupply -ErrorAction SilentlyContinue).Status"
        res_psu = subprocess.run(["powershell", "-Command", cmd_psu], capture_output=True, text=True, timeout=5)
        
        if res_psu.stdout.strip():
            psu_status = res_psu.stdout.strip().upper()
        else:
            cmd_status = "(Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue).BatteryStatus"
            res_status = subprocess.run(["powershell", "-Command", cmd_status], capture_output=True, text=True, timeout=5)
            if "2" in res_status.stdout:
                psu_status = "CONECTADO"
            elif "1" in res_status.stdout:
                psu_status = "NA BATERIA"
    except:
        pass

    if psu_status != "N/A":
        cor = 32 if psu_status in ["OK", "CONECTADO"] else 33
        print(f"Status da Fonte:      " + print_colored(psu_status, cor))
    else:
        print("Status da Fonte:      N/A (Sensor não disponível)")

def exibir_detalhes_ram():
    log_header("DETALHES DA MEMÓRIA RAM E SISTEMA LOCAL")
    """Analisa velocidade e geração dos pentes de memória."""
    ram_cmd = 'Get-WmiObject Win32_PhysicalMemory | ForEach-Object { $t = $_.MemoryType; if($t -eq 0){$t = $_.SMBIOSMemoryType}; $gen = switch($t){20{"DDR"};21{"DDR2"};24{"DDR3"};26{"DDR4"};34{"DDR5"};default{"Outra"}}; "{0} MHz | {1} | {2} GB" -f $_.Speed, $gen, ([math]::round($_.Capacity / 1GB, 2)) }'
    ram_out = run_ps(ram_cmd)
    
    print("\nDetalhes da Memória RAM:")
    if ram_out:
        print(f"{'Velocidade':<10} | {'Geração':<10} | {'Capacidade'}")
        print("-" * 35)
        print(ram_out)
    else:
        # Fallback caso o comando complexo falhe
        total_ram = round(psutil.virtual_memory().total / (1024**3), 2)
        print_warning(f"Total detectado: {total_ram} GB (Informações detalhadas via WMI indisponíveis)")
    
    print ("\n" + "-"*60)

    # Tempo de atividade (Se o PC está ligado há 10 dias, por isso está lento)
    uptime_cmd = '$u = (Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime; "{0} dias, {1} horas e {2} min" -f $u.Days, $u.Hours, $u.Minutes'
    uptime_str = run_ps(uptime_cmd)
    print(f"\nUltimo boot do Sistema: " + print_colored(uptime_str, C_CYAN))
    if not uptime_str:
        print_warning("Não foi possível obter o tempo desde o último boot.")
    
    #IP local
    ip_cmd = "Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Ethernet*' | Where-Object {$_.IPAddress -ne '127.0.0.1'} | ForEach-Object { $_.IPAddress }"
    ip_address = run_ps(ip_cmd)
    print(f"\nEndereço IP Local: "+ print_colored(ip_address, C_CYAN))
    if not ip_address:
        print_warning("Não foi possível obter o endereço IP local.")


def data_formatacao():
    log_header("DATA DE INSTALAÇÃO DO WINDOWS")
    cmd_ps = "([WMI]'').ConvertToDateTime((Get-WmiObject Win32_OperatingSystem).InstallDate)"
    
    install_date = run_ps(cmd_ps)
    print(f"Sistema operacional instalado em: " + print_colored(install_date, C_GREEN))

def diagnostico_latencia_media():
    log_header("MÉDIA DE RESPOSTA DA REDE (LATÊNCIA)")
    destinos = ["8.8.8.8", "www.google.com"]
    
    for alvo in destinos:
        print(f"A medir latência média para {alvo}...")
        tempos = []
        
        for _ in range(4):
            res = subprocess.run(["ping", "-n", "1", alvo], capture_output=True, text=True, errors='replace')
            if res.returncode == 0:
                match = re.search(r"(?:tempo|time)\s*=\s*(\d+)\s*ms", res.stdout, re.IGNORECASE)
                if match:
                    tempos.append(int(match.group(1)))
            time.sleep(0.5) 

        if tempos:
            media = sum(tempos) / len(tempos)
            cor = C_GREEN if media < 50 else C_YELLOW if media < 150 else C_RED
            status = "Excelente" if media < 50 else "Instável" if media < 150 else "Lenta"
            print(f"  -> {alvo}: " + print_colored(f"{media:.1f} ms ({status})", cor))
        else:
            print_warning(f"  -> {alvo}: Sem resposta (Falha na conexão)")

def listar_janelas_ativas():
    log_header("JANELAS ABERTAS NO MOMENTO")
    cmd = 'Get-Process | Where-Object {$_.MainWindowTitle} | ForEach-Object { "$($_.Id);$($_.ProcessName);$($_.Responding);$($_.MainWindowTitle)" }'
    janelas_out = run_ps(cmd)
    
    lines = janelas_out.splitlines()
    if lines:
        print(f"{'PID':<8} | {'Status':<12} | {'Executável':<15} | {'Título da Janela'}")
        print("-" * 85)
        for line in lines:
            parts = line.split(';', 3)
            if len(parts) == 4:
                pid, name, resp, title = parts
                status = "Ativo" if resp == "True" else "Não Responde" if resp == "False" else "Desconhecido"
                print(f"{pid:<8} | {status:<12} | {name:<15} | {title}")
    else:
        print_warning("Nenhuma janela de aplicativo detectada no momento.")

if __name__ == "__main__":
    # Habilita suporte a ANSI no Windows uma única vez
    if os.name == 'nt':
        ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)

    try:
        print("EXECUTANDO DIAGNÓSTICO RÁPIDO...")
        diagnosticar_processos()
        verificar_usuarios_locais()
        exibir_saude_discos ()
        exibir_saude_energia()  
        exibir_detalhes_ram()
        data_formatacao()
        listar_janelas_ativas()
        diagnostico_latencia_media()
        status_seguranca()
        print("\n" + "="*30)
        input(print_colored("\n[!] Diagnóstico finalizado. Pressione Enter para sair...", C_GREEN))
    except Exception as e:
        print(print_colored(f"\n[ERRO CRÍTICO]: {str(e)}", C_RED))
        traceback.print_exc()
        print("\n" + "="*30)
        input("Pressione Enter para fechar...")
