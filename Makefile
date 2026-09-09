PYTHON ?= python3
.PHONY: test demo generate hmda stack-up stack-down dbt-build local-db-start local-db-stop pipeline clean-artifacts
test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -p 'test*.py' -v
integration-test:
	RUN_DB_TESTS=1 PYTHONPATH=src $(PYTHON) -m unittest tests.integration.test_postgres_pipeline -v
demo:
	PYTHONPATH=src python3 -m metric_hub.cli --allow-drift
generate:
	PYTHONPATH=src python3 pipelines/generate_data.py --rows 50000 --seed 2026
hmda:
	PYTHONPATH=src $(PYTHON) pipelines/prepare_hmda.py --rows 2800000
stack-up:
	docker compose up -d --wait
stack-down:
	docker compose down
dbt-build:
	DBT_PROFILES_DIR=dbt dbt build --project-dir dbt
local-db-start:
	./scripts/start_local_postgres.sh
local-db-stop:
	./scripts/stop_local_postgres.sh
pipeline: local-db-start
	PYTHONPATH=src $(PYTHON) pipelines/run_pipeline.py --rows 50000 --seed 2026
clean-artifacts:
	find data/raw data/processed data/manifests reports dashboard screenshots logs -type f -delete
