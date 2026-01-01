.PHONY: up down restart logs ps shell trigger help init

help:
	@echo "Available commands:"
	@echo "  make init     - Initialize Airflow (create folders, set permissions)"
	@echo "  make up       - Start Airflow containers in background"
	@echo "  make down     - Stop and remove Airflow containers"
	@echo "  make restart  - Restart Airflow containers"
	@echo "  make logs     - View container logs (follow)"
	@echo "  make ps       - List running containers"
	@echo "  make shell    - Open bash shell in airflow-scheduler"
	@echo "  make trigger  - Trigger the 'sample_failing_dag'"

airflow-init:
	docker compose up airflow-init

airflow-up:
	docker compose up -d

airflow-down:
	docker compose down

airflow-logs:
	docker compose logs -f airflow-scheduler

service:
	uv run uvicorn oncall_agent.src.service.main:app --reload --port 8000
