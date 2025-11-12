"""In-memory TF-IDF retrieval over processed recipes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Retriever:
    def __init__(
        self,
        recipes: List[Dict[str, Any]],
        vectorizer: TfidfVectorizer | None,
        matrix,
    ) -> None:
        self.all_recipes = recipes
        self._vectorizer = vectorizer
        self._matrix = matrix

    @classmethod
    def from_processed(cls, path: str = "data/processed") -> "Retriever":
        base_path = Path(path)
        json_path = base_path / "recipes_enriched.json"
        if not json_path.exists():
            raise FileNotFoundError(f"Missing processed file at {json_path}")

        with json_path.open("r", encoding="utf-8") as handle:
            recipes: List[Dict[str, Any]] = json.load(handle)

        texts = [
            (
                f"{recipe.get('title', '')} "
                f"{' '.join(recipe.get('ingredients_norm', []))}"
            ).strip()
            for recipe in recipes
        ]

        if recipes:
            vectorizer = TfidfVectorizer(stop_words="english")
            matrix = vectorizer.fit_transform(texts)
        else:
            vectorizer = None
            matrix = None

        return cls(recipes=recipes, vectorizer=vectorizer, matrix=matrix)

    def search(self, query_tokens: List[str], top_k: int) -> List[Dict[str, Any]]:
        if not self.all_recipes:
            return []

        limit = min(top_k, len(self.all_recipes))
        if not query_tokens or self._matrix is None or self._vectorizer is None:
            return self.all_recipes[:limit]

        query = " ".join(query_tokens)
        query_vec = self._vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self._matrix).flatten()
        ranked_indices = similarities.argsort()[::-1][:limit]
        ranked_recipes = []
        for idx in ranked_indices:
            recipe = dict(self.all_recipes[idx])
            recipe["similarity"] = float(similarities[idx])
            ranked_recipes.append(recipe)
        return ranked_recipes
