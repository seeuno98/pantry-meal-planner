PYTHON ?= python3

.PHONY: up down api spark-etl test format lint

up:
	docker compose -f infra/docker/docker-compose.yml up -d

down:
	docker compose -f infra/docker/docker-compose.yml down -v

api:
	uvicorn src.api.main:app --reload --port 8000

spark-etl:
	$(PYTHON) -m src.pipelines.spark.jobs.etl_recipes --recipes data/raw/recipes/recipes_sample.json --usda data/raw/usda/usda_lookup.csv --out data/processed

test:
	pytest -q

format:
	black src tests

lint:
	ruff src tests
