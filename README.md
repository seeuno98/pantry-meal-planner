````markdown
# Pantry-Aware Meal Planner (MLOps RAG)
Pantry-aware recipe recommendations with macro targets, substitution tips, and a deduped grocery list. FastAPI + Spark ETL + Qdrant/OpenSearch + Redis cache + Prometheus/Grafana. Optional OpenAI mini for top-K explanations.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make up           # start dockerized infra (api, redis, qdrant, opensearch, prometheus, grafana)
make api          # run FastAPI locally
# open http://localhost:8000/docs and http://localhost:8000/metrics
````

