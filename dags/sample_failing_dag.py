from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models.param import Param
from datetime import datetime
import requests
import os

# Mock Logs for Scenarios
MOCK_LOGS = {
    "time_out_error": "ERROR - Task failed due to timeout. Execution time exceeded threshold of 3600s after 1 attempt.",
    "DQcheck_failure": "ERROR - DataQualityCheckFailed: null values in 'user_id' detected in 'raw_events' (total 45 rows affected).",
    "file_not_found": "ERROR - FileNotFoundError: [Errno 2] No such file or directory: 's3://production-bucket/logs/2024-01-01/activity.csv'",
    "upstream_DAG_failure": "ERROR - Task dependency failure. Upstream task 'validate_schema' failed with exit code 1.",
    "cluster_error": "ERROR - ClusterConnectionError: connection timed out while connecting to worker node 10.0.4.15."
}

# Define the callback function
def notify_oncall_agent(context):
    """
    Callback to alert the OnCall Agent running on the host machine.
    """
    agent_url = os.getenv("ONCALL_AGENT_URL", "http://host.docker.internal:8000/analyze")
    
    task_instance = context.get('task_instance')
    dag_run = context.get('dag_run')
    exception = context.get('exception')
    
    # Get selected scenario from params
    scenario = dag_run.conf.get('failure_scenario') if dag_run.conf else None
    
    # Check for manual logs override
    manual_logs = dag_run.conf.get('logs') if dag_run.conf else None
    
    # Determine the log content to send
    if manual_logs:
        log_content = manual_logs
    elif scenario and scenario in MOCK_LOGS:
        log_content = MOCK_LOGS[scenario]
    else:
        log_content = str(exception)
    
    payload = {
        "source_system": "airflow",
        "incident_id": f"{dag_run.run_id}::{task_instance.task_id}",
        "title": f"Airflow Task Failed: {task_instance.task_id}",
        "description": f"DAG: {dag_run.dag_id} failed on task {task_instance.task_id}. Selected Scenario: {scenario or 'General Error'}",
        "logs": log_content,
        "metadata": {
            "dag_id": dag_run.dag_id,
            "run_id": dag_run.run_id,
            "task_id": task_instance.task_id,
            "scenario": scenario,
            "original_exception": str(exception)
        }
    }
    
    print(f"Sending alert to {agent_url} for scenario: {scenario}...")
    try:
        response = requests.post(agent_url, json=payload, timeout=5)
        print(f"Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to alert agent: {e}")

# Define the DAG
default_args = {
    'owner': 'data_engineering',
    'start_date': datetime(2024, 1, 1),
    'on_failure_callback': notify_oncall_agent
}

with DAG('sample_failing_dag', 
         default_args=default_args, 
         schedule='@daily', 
         params={
             "failure_scenario": Param(
                 default="time_out_error",
                 type="string",
                 enum=["time_out_error", "DQcheck_failure", "file_not_found", "upstream_DAG_failure", "cluster_error"],
                 description="Select the failure case to simulate."
             )
         },
         catchup=False) as dag:

    def stable_task():
        print("This task runs fine.")

    def failing_task(**context):
        scenario = context['params'].get('failure_scenario', 'generic_error')
        print(f"Simulating failure scenario: {scenario}")
        
        # Raise an exception containing the scenario name so it's traceable
        raise RuntimeError(f"Simulated Failure: {scenario}")

    t1 = PythonOperator(
        task_id='ingest_data',
        python_callable=stable_task
    )

    t2 = PythonOperator(
        task_id='process_data',
        python_callable=failing_task,
        provide_context=True
    )

    t1 >> t2
