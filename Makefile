.PHONY: test demo generate stack-up stack-down dbt-build
test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v
demo:
	PYTHONPATH=src python3 -m metric_hub.cli; test $$? -eq 1
generate:
	python3 data_generator/generate.py --rows 10000 --seed 2026
stack-up:
	docker compose up -d --wait
stack-down:
	docker compose down
dbt-build:
	DBT_PROFILES_DIR=dbt dbt build --project-dir dbt
