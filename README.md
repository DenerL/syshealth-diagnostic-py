# 📊 System Health Diagnostic & Data Pipeline

This repository contains a dual-purpose IT infrastructure solution designed to streamline local system diagnostics and automate data ingestion for long-term monitoring.

---

## 📂 Project Architecture

The project is structured into two independent modules based on the deployment requirements:

### 1. 🛠️ Local Diagnostic Tool (`/local_tool`)
* **Purpose:** Developed for on-site IT support and quick infrastructure auditing.
* **How it works:** A lightweight script designed to be run directly from a flash drive or network share. It performs a real-time hardware and network health check, outputting clean, actionable diagnostics directly to the terminal for immediate troubleshooting.

### 2. 🗄️ Infrastructure Data Pipeline (`/data_pipeline`)
* **Purpose:** Built for data engineering and systems telemetry monitoring.
* **How it works:** An automated pipeline that collects system metrics, processes the data types, and ingests the logs into a local **SQLite database** (`telemetria_infra.db`). It includes dedicated scripts for database initialization, data ingestion, and historical query visualization.

---

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **OS Integration:** PowerShell API / Windows CIM (Couch Information Model)
* **Database:** SQLite 3
* **Libraries:** `psutil`, `sqlite3`, `subprocess`, `re`

---

## 🚀 How to Run

### 🛠️ Local Diagnostics

Execute the following command to run the on-site diagnostic tool:

* **Command:** `python local_tool/diagnostico_local.py`

---

### 🗄️ Data Pipeline (Ingestion & Visualization)

Follow these steps in order to initialize, ingest, and check the database:

1. **Initialize the database:** `python data_pipeline/criar_banco.py`
2. **Capture and ingest data:** `python data_pipeline/capturar_dados.py`
3. **View historical records:** `python data_pipeline/visualizar_dados.py`

---

*To check my latest code updates, contributions, and project repositories, please navigate to the **Repositories** tab above.*
