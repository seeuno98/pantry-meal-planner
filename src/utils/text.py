"""Text normalization helpers shared between ETL and API layers."""

from __future__ import annotations

import re
from typing import Iterable, List

_PUNCT_PATTERN = re.compile(r"[^a-z0-9\s]")
_SPACE_PATTERN = re.compile(r"\s+")
_STOP_TOKENS = {"", "and", "with"}


def _singularize(token: str) -> str:
    if token.endswith("ies") and len(token) > 3:
        return token[:-3] + "y"
    if token.endswith("es") and len(token) > 2:
        return token[:-2]
    if token.endswith("s") and len(token) > 2:
        return token[:-1]
    return token


def normalize_token(token: str) -> str:
    """Lower, strip punctuation, collapse spaces, and singularize basic plurals."""
    lowered = _PUNCT_PATTERN.sub(" ", token.lower())
    lowered = _SPACE_PATTERN.sub(" ", lowered).strip()
    return _singularize(lowered)


def normalize_tokens(text: str) -> List[str]:
    """Tokenize and normalize a free-form text snippet."""
    normalized = normalize_token(text)
    tokens = [tok for tok in normalized.split(" ") if tok not in _STOP_TOKENS]
    return [tok for tok in tokens if tok]


def normalize_ingredient_list(ingredients: Iterable[str]) -> List[str]:
    """Normalize a list of ingredient strings and keep order without duplicates."""
    seen = set()
    normalized_tokens: List[str] = []
    for item in ingredients:
        for token in normalize_tokens(item):
            if token not in seen:
                seen.add(token)
                normalized_tokens.append(token)
    return normalized_tokens
