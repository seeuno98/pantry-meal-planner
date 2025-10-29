up:
	docker compose -f infra/docker/docker-compose.yml up -d

down:
	docker compose -f infra/docker/docker-compose.yml down -v

api:
	uvicorn src.api.main:app --reload

spark-etl:
	python src/pipelines/spark/jobs/etl_recipes.py && \
	python src/pipelines/spark/jobs/etl_usda.py && \
	python src/pipelines/spark/jobs/features_join.py
