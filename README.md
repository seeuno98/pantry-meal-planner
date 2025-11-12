# Pantry Meal Planner (MVP)

FastAPI service that plans meals from your pantry, scores recipes with macro targets, and outputs a deduped grocery list. Everything runs **locally** with seed data, a Spark ETL job, and an in-memory TF-IDF retriever.

---

## 🚦 Project Stages

### Stage 1 — MVP (this branch)

Local-only planner with seed data.

* **Data**: local JSON/CSV → Spark ETL → `data/processed/`
* **Retrieval**: in-memory TF-IDF (scikit-learn)
* **Scoring**: pantry-coverage + macro-fit (deterministic)
* **API**: FastAPI endpoints (`/plan/meals`, `/health`, `/metrics`)
* **Infra**: none (no LangChain, no AWS, no Redis/Qdrant)

### Stage 2 — Cloud & LLM Add-ons (next branch)

Optional, backwards-compatible features toggled by config:

* **LLM explanations & substitutions**: LangChain + OpenAI/Anthropic/HF
* **Vector search**: Qdrant or OpenSearch (hybrid BM25 + embeddings)
* **Storage**: S3 for `raw/` & `processed/` artifacts
* **Orchestration**: Airflow (MWAA) or ECS scheduled jobs for nightly ETL
* **Serving**: Dockerized API on ECS Fargate (or EKS), API Gateway/ALB
* **Observability**: CloudWatch (plus optional Prometheus/Grafana)
* **CI/CD**: GitHub Actions → ECR → ECS; optional Terraform for IaC

---

## 🧱 Stack at a Glance (MVP)

* **Data:** `data/raw/recipes/recipes_sample.json` (~200 recipes) + `data/raw/usda/usda_lookup.csv`
* **ETL:** PySpark job normalizes ingredients, enriches missing macros, and writes `data/processed/recipes_enriched.{parquet,json}`
* **Retrieval:** `scikit-learn` TF-IDF vectors over title + normalized ingredients
* **Scoring:** Pantry coverage + macro fit (sigmoid on protein, calorie penalty) → deterministic ordering
* **API:** FastAPI with `/health`, `/metrics`, and `/plan/meals`
* **Tests:** Pytest smoke tests for planner behavior

---

## ⚡ Quickstart (MVP)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Build processed artifacts (Spark)
make spark-etl

# Run the API locally
make api
# Open http://localhost:8000/docs for OpenAPI + examples

# Developer utilities
make test      # pytest -q
make lint      # ruff src tests
make format    # black src tests
```

**Note:** Ensure the seed data exists at:

```
data/raw/recipes/recipes_sample.json
data/raw/usda/usda_lookup.csv
```

---

## ⚙️ Configuration

All tunables live in `configs/dev.yaml`:

```yaml
retrieval:
  top_k: 50
scoring:
  w_coverage: 0.6
  w_macro: 0.4
features:
  cache_ttl_seconds: 0
  llm_explanations: false     # Phase 2 (off in MVP)
  remote_vector_search: false # Phase 2 (off in MVP)
  s3_storage: false           # Phase 2 (off in MVP)
providers:
  llm: openai                  # openai|anthropic|hf (Phase 2)
  vector: tfidf                # tfidf|qdrant|opensearch
  storage: local               # local|s3
paths:
  processed_dir: data/processed
aws:
  region: us-west-2
  s3_bucket: your-bucket
  s3_prefix: pantry-meal-planner/
```

---

## 🌐 API

### `POST /plan/meals`

**Request**

```json
{
  "pantry": ["chicken", "rice", "garlic"],
  "targets": {"protein_g_min": 25, "kcal_max": 650},
  "days": 3,
  "servings": 2,
  "avoid": ["peanut"],
  "prefer": ["herb"]
}
```

**Response**

```json
{
  "recipes": [
    {
      "id": "recipe-001",
      "title": "Garlic Chicken Breast Bowl",
      "ingredients": ["chicken breast", "rice (white, cooked)", "garlic", "olive oil", "..."],
      "est_kcal": 410,
      "est_protein_g": 38.0,
      "score": 0.78
    }
  ],
  "grocery_list": [
    {"item": "parsley", "aisle": "produce", "qty": null}
  ]
}
```

**Other Endpoints**

* `GET /health` → `{"ok": true}`
* `GET /metrics` → `{"plans_served": <int>}`

OpenAPI docs with examples at `/docs`.

---

## 🛠️ Development Notes

* Run ETL first (`make spark-etl`) to generate `data/processed/recipes_enriched.{parquet,json}` before calling the API or tests.
* Retrieval is fully in-memory; no Redis, Qdrant, or OpenSearch instances are required in MVP.
* Grocery list builder heuristically assigns aisles (produce/meat/pantry/dairy/bakery) and removes pantry/avoid items.

---

## ✅ Testing

`tests/test_plan_api.py` boots the FastAPI app with `TestClient` and validates:

1. Happy-path response structure and grocery list
2. `avoid` tokens excluded from suggestions
3. Empty pantry still yields five ranked recipes

Run `make test` after `make spark-etl`.

---

## 🗺️ Roadmap

* [x] MVP API with TF-IDF retrieval and local ETL
* [ ] Provider switch: `providers.vector = tfidf|qdrant|opensearch`
* [ ] S3 storage toggle: `features.s3_storage = true`
* [ ] LLM explanations toggle: `features.llm_explanations = true`
* [ ] Dockerize API; GitHub Actions → ECR
* [ ] ECS Fargate deploy; API Gateway + ALB
* [ ] MWAA (Airflow) nightly ETL
* [ ] Observability: CloudWatch metrics/logs
