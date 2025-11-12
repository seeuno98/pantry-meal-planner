"""Grocery list builder based on recipe gaps."""
from __future__ import annotations

from typing import Dict, List


AISLE_KEYWORDS = {
    "produce": ["garlic", "onion", "parsley", "basil", "lemon", "lime", "salad"],
    "meat": ["chicken", "turkey", "beef", "pork", "salmon", "shrimp"],
    "pantry": ["rice", "quinoa", "noodle", "pasta", "olive", "oil", "salt", "pepper", "chili", "paprika", "lentil", "chickpea"],
    "dairy": ["egg", "cheese", "yogurt"],
    "bakery": ["tortilla", "bread"],
}


def _guess_aisle(token: str) -> str:
    for aisle, keywords in AISLE_KEYWORDS.items():
        if any(keyword in token for keyword in keywords):
            return aisle
    return "pantry"


def build_grocery_list(recipes: List[Dict], pantry_tokens: List[str], avoid: List[str]) -> List[Dict]:
    """
    Missing = ingredients_norm − pantry_tokens − avoid.
    Heuristic aisle mapping (dict of keywords → 'produce'/'meat'/'pantry'/'dairy'/'bakery').
    Deduplicate and sort alphabetically.
    """

    pantry_set = set(pantry_tokens)
    avoid_set = set(avoid)

    missing = set()
    for recipe in recipes:
        for token in recipe.get("ingredients_norm", []) or []:
            if token not in pantry_set and token not in avoid_set:
                missing.add(token)

    grocery_items = [
        {"item": token, "aisle": _guess_aisle(token), "qty": None}
        for token in sorted(missing)
    ]
    return grocery_items
