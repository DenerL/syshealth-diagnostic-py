# syshealth-diagnostic-py
Ferramenta de automação para diagnóstico de hardware, rede e segurança em ambientes Windows utilizando Python e PowerShell.

# 🛠️ SysHealth Diagnostic Tool

Ferramenta de automação desenvolvida para otimizar o suporte técnico e a coleta de telemetria em parques tecnológicos Windows.

## 📋 O Problema
Em ambientes de suporte, o diagnóstico manual de hardware e rede é lento e descentralizado. Máquinas com lentidão por falta de reboot, desgaste de SSD ou latência de rede impactam diretamente na produtividade da operação.

## 💡 A Solução
Um script robusto que atua como um orquestrador de dados, utilizando Python para gerenciar execuções de baixo nível via PowerShell (WMI/CIM). A ferramenta consolida informações críticas em segundos, permitindo uma tomada de decisão rápida baseada em dados reais.

## 🚀 Funcionalidades Técnicas

Ranking de Processos: Identificação de "vilões" de memória RAM usando psutil.

Saúde de Disco: Monitoramento de vida útil de SSDs (Wear Leveling) e espaço em disco.

Telemetria de Energia: Lógica de cascata para detectar saúde de bateria e status da fonte em notebooks e desktops.

Análise de Rede: Teste de latência média (ping) para isolar problemas de infraestrutura.

Segurança: Verificação de privilégios de administradores locais e status do antivírus.

## 🛠️ Tecnologias Utilizadas

Python 3.x (Lógica principal e tratamento de dados)

PowerShell/WMI (Interface com o hardware)

Regex (Limpeza e extração de dados brutos)

Bibliotecas: psutil, subprocess, ctypes

## 📊 Casos de Uso (Data Insights)
Este script não é apenas para suporte, ele é a base para:
- **Gestão de Ativos:** Identificar máquinas que precisam de upgrade de RAM ou SSD.
- **Prevenção de Downtime:** Detectar SSDs com alto nível de desgaste antes que falhem.
- **Segurança de Dados:** Auditar quem são os administradores locais de cada máquina.

## 🚀 Como Executar
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute com privilégios de Administrador: `python src/Saude_hardware.py`

## 🖥️ Demonstração do Terminal
 <img width="969" height="488" alt="Captura de tela 2026-05-19 092632" src="https://github.com/user-attachments/assets/1a0ec29d-3e04-4c3f-bf8e-1bfc593967b5" />

