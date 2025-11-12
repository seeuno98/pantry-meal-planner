from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.pipelines.spark.jobs.etl_recipes import run_etl

RECIPES_PATH = "data/raw/recipes/recipes_sample.json"
USDA_PATH = "data/raw/usda/usda_lookup.csv"
PROCESSED_DIR = "data/processed"


@pytest.fixture(scope="session", autouse=True)
def ensure_processed_data() -> None:
    processed_json = Path(PROCESSED_DIR) / "recipes_enriched.json"
    if not processed_json.exists():
        run_etl(RECIPES_PATH, USDA_PATH, PROCESSED_DIR)


@pytest.fixture(scope="session")
def client(ensure_processed_data) -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_plan_meals_happy_path(client: TestClient) -> None:
    payload = {
        "pantry": ["chicken", "rice", "garlic"],
        "targets": {"protein_g_min": 25, "kcal_max": 700},
    }
    response = client.post("/plan/meals", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert 1 <= len(body["recipes"]) <= 5
    for recipe in body["recipes"]:
        for key in ["id", "title", "ingredients", "est_kcal", "est_protein_g", "score"]:
            assert key in recipe
    assert body["grocery_list"]


def test_plan_meals_avoid_tokens(client: TestClient) -> None:
    payload = {
        "pantry": ["shrimp", "rice"],
        "targets": {"protein_g_min": 20, "kcal_max": 650},
        "avoid": ["peanut", "shellfish"],
    }
    response = client.post("/plan/meals", json=payload)
    assert response.status_code == 200
    body = response.json()
    avoid_terms = {"peanut", "shellfish"}
    for recipe in body["recipes"]:
        ingredients = " ".join(ing.lower() for ing in recipe["ingredients"])
        assert not any(term in ingredients for term in avoid_terms)


def test_plan_meals_low_pantry(client: TestClient) -> None:
    payload = {
        "pantry": [],
        "targets": {"protein_g_min": 25, "kcal_max": 700},
    }
    response = client.post("/plan/meals", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["recipes"]) == 5
