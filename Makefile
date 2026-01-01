.PHONY: airflow-up airflow-down airflow-logs airflow-restart airflow-init trigger help ps shell

help:
	@echo "Available commands:"
	@echo "  make airflow-init    - Initialize Airflow (create folders, set permissions)"
	@echo "  make airflow-up      - Start Airflow containers in background"
	@echo "  make airflow-down    - Stop and remove Airflow containers"
	@echo "  make airflow-restart - Restart Airflow containers"
	@echo "  make airflow-logs    - View container logs (follow scheduler)"
	@echo "  make ps              - List running containers"
	@echo "  make shell           - Open bash shell in airflow-scheduler"
	@echo "  make trigger         - Trigger the 'sample_failing_dag'"

airflow-init:
	docker compose up airflow-init

airflow-up:
	docker compose up -d

airflow-down:
	docker compose down

airflow-restart:
	docker compose restart

airflow-logs:
	docker compose logs -f airflow-scheduler

ps:
	docker compose ps

shell:
	docker compose exec airflow-scheduler bash

trigger:
	docker compose exec airflow-scheduler airflow dags trigger sample_failing_dag
