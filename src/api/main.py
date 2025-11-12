"""FastAPI application for the Pantry Meal Planner MVP."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from fastapi import FastAPI, HTTPException

from src.utils.text import normalize_ingredient_list

from .config import config
from .schemas import PlanRequest, PlanResponse, RecipeOut
from .services.grocery import build_grocery_list
from .services.retrieval import Retriever
from .services.score import score_recipes

app = FastAPI(
    title="Pantry Meal Planner",
    description="Suggest pantry-aware recipes and a deduped grocery list.",
)

plans_served = 0


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    processed_dir = config.paths.processed_dir
    return Retriever.from_processed(processed_dir)


def _normalize_list(items: List[str]) -> List[str]:
    return normalize_ingredient_list(items or [])


@app.get("/health")
def health() -> dict:
    """Simple health probe."""
    return {"ok": True}


@app.get("/metrics")
def metrics() -> dict:
    """Expose minimal in-memory counters for future Prometheus scrape."""
    return {"plans_served": plans_served}


@app.post("/plan/meals", response_model=PlanResponse)
def plan_meals(request: PlanRequest) -> PlanResponse:
    """
    Plan meals around pantry items and macro targets.

    Example request:
    {
        "pantry": ["chicken", "rice", "garlic"],
        "targets": {"protein_g_min": 25, "kcal_max": 650},
        "avoid": ["peanut"],
        "prefer": ["herb"]
    }

    Example response:
    {
        "recipes": [{"id": "recipe-001", "title": "Garlic Chicken Bowl", "score": 0.78, ...}],
        "grocery_list": [{"item": "parsley", "aisle": "produce"}]
    }
    """

    pantry_tokens = _normalize_list(request.pantry)
    prefer_tokens = _normalize_list(request.prefer)
    avoid_tokens = set(_normalize_list(request.avoid))
    query_tokens = pantry_tokens + prefer_tokens

    try:
        retriever = get_retriever()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="Processed data missing. Run `make spark-etl` before calling the API.",
        ) from exc

    candidates = retriever.search(
        query_tokens=query_tokens, top_k=config.retrieval.top_k
    )

    def _contains_avoids(recipe: dict) -> bool:
        tokens = recipe.get("ingredients_norm", [])
        return any(token in avoid_tokens for token in tokens)

    filtered_candidates = [
        recipe for recipe in candidates if not _contains_avoids(recipe)
    ]
    if not filtered_candidates:
        filtered_candidates = [
            recipe for recipe in retriever.all_recipes if not _contains_avoids(recipe)
        ]

    scored = score_recipes(
        candidates=filtered_candidates,
        pantry_tokens=pantry_tokens,
        protein_min=request.targets.protein_g_min,
        kcal_max=request.targets.kcal_max,
        w_coverage=config.scoring.w_coverage,
        w_macro=config.scoring.w_macro,
    )
    top_recipes = scored[:5]
    grocery_list = build_grocery_list(top_recipes, pantry_tokens, list(avoid_tokens))

    recipe_models = [
        RecipeOut(
            id=recipe["id"],
            title=recipe["title"],
            ingredients=recipe.get("ingredients", []),
            est_kcal=int(recipe.get("est_kcal") or 0),
            est_protein_g=int(recipe.get("est_protein_g") or 0),
            score=round(float(recipe.get("score", 0.0)), 4),
        )
        for recipe in top_recipes
    ]

    global plans_served
    plans_served += 1

    return PlanResponse(recipes=recipe_models, grocery_list=grocery_list)
