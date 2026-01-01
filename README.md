# OnCallAirflow

This repository contains a containerized Apache Airflow environment used to demonstrate and test the **AI-powered Data Engineering OnCall Agent**.

## 🚀 Overview

The environment is built using Docker Compose and follows the official Airflow reference architecture, utilizing the `CeleryExecutor` with PostgreSQL and Redis. It includes a custom "on-failure" integration that triggers the AI Agent to diagnose and remediate pipeline failures.

## 🛠️ Features

- **Airflow 2.10.4**: Pre-configured local cluster.
- **Automated Diagnosis**: Integrated with an external AI Agent service via task callbacks.
- **Reference DAGs**: Includes `sample_failing_dag` to simulate various failure scenarios (Transient, Permanent, DQ).
- **Simplified CLI**: Easy-to-use `Makefile` for common operations.

## 📋 Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🏁 Getting Started

### 1. Initialize the Environment
This creates the necessary directories and initializes the Airflow database.
```bash
make airflow-init
```

### 2. Start Airflow
Launch all containers (Webserver, Scheduler, Worker, Redis, Postgres) in the background.
```bash
make airflow-up
```

### 3. Access the UI
Open your browser and navigate to:
- **URL**: [http://localhost:8080](http://localhost:8080)
- **Login**: `airflow` / `airflow`

## 🎛️ Makefile Commands

| Command | Description |
| :--- | :--- |
| `make airflow-init` | Initialize folders, permissions, and database. |
| `make airflow-up` | Start all Airflow services. |
| `make airflow-down` | Stop and remove containers. |
| `make airflow-logs` | Follow scheduler logs. |
| `make trigger` | Manually trigger the `sample_failing_dag`. |
| `make shell` | Open a bash shell inside the scheduler container. |

## 📂 Project Structure

- `dags/`: Python DAG definitions (includes the failing samples).
- `config/`: Airflow and service configurations.
- `plugins/`: Custom Airflow plugins.
- `logs/`: Mounted volume for task execution logs.

## 🤖 AI Agent Integration

This environment is designed to work with the `OnCallAgent` service. When a task in the `sample_failing_dag` fails:
1. The `on_failure_callback` captures the error context and logs.
2. It sends a POST request to the AI Agent API (running on port 8000 by default).
3. The Agent analyzes the failure and suggests/executes remediation.
