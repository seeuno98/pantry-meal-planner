"""Configuration loader for the Pantry Meal Planner API."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class RetrievalConfig:
    top_k: int = 50


@dataclass
class ScoringConfig:
    w_coverage: float = 0.6
    w_macro: float = 0.4


@dataclass
class FeatureConfig:
    cache_ttl_seconds: int = 0


@dataclass
class PathConfig:
    processed_dir: str = "data/processed"


@dataclass
class AppConfig:
    retrieval: RetrievalConfig
    scoring: ScoringConfig
    features: FeatureConfig
    paths: PathConfig


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_config(path: str = "configs/dev.yaml") -> AppConfig:
    cfg_path = Path(path)
    data = _load_yaml(cfg_path)
    retrieval = RetrievalConfig(**data.get("retrieval", {}))
    scoring = ScoringConfig(**data.get("scoring", {}))
    features = FeatureConfig(**data.get("features", {}))
    paths = PathConfig(**data.get("paths", {}))
    return AppConfig(retrieval=retrieval, scoring=scoring, features=features, paths=paths)


config = load_config()
