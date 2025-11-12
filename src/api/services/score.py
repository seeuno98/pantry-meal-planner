"""Deterministic scoring utilities for recipes."""
from __future__ import annotations

import math
from typing import Dict, List


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def score_recipes(
    candidates: List[Dict],
    pantry_tokens: List[str],
    protein_min: int,
    kcal_max: int,
    w_coverage: float,
    w_macro: float,
) -> List[Dict]:
    """
    Adds 'score' field and returns sorted list (desc).
    coverage = |ingredients_norm ∩ pantry_tokens| / max(1, |ingredients_norm|)
    macro_fit = sigmoid((protein - protein_min)/max(protein_min,1)) - penalty if kcal > kcal_max
    final = w_coverage*coverage + w_macro*macro_fit
    """

    pantry_set = set(pantry_tokens)
    scored: List[Dict] = []
    kcal_cap = max(kcal_max, 1)
    protein_cap = max(protein_min, 1)

    for recipe in candidates:
        norm_tokens = recipe.get("ingredients_norm", []) or []
        overlap = len(pantry_set.intersection(norm_tokens))
        coverage = overlap / max(1, len(norm_tokens))

        protein = float(recipe.get("est_protein_g") or 0)
        kcal = float(recipe.get("est_kcal") or 0)
        macro_fit = sigmoid((protein - protein_cap) / protein_cap)

        if kcal > kcal_cap * 1.1:
            macro_fit -= 0.3
        elif kcal > kcal_cap:
            macro_fit -= 0.15

        final_score = w_coverage * coverage + w_macro * macro_fit

        enriched = dict(recipe)
        enriched["coverage"] = coverage
        enriched["macro_fit"] = macro_fit
        enriched["score"] = final_score
        scored.append(enriched)

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored
