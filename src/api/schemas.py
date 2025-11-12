from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Targets(BaseModel):
    protein_g_min: int
    kcal_max: int


class PlanRequest(BaseModel):
    pantry: List[str] = Field(default_factory=list)
    targets: Targets
    days: int = 3
    servings: int = 2
    avoid: List[str] = Field(default_factory=list)
    prefer: List[str] = Field(default_factory=list)


class RecipeOut(BaseModel):
    id: str
    title: str
    ingredients: List[str]
    est_kcal: int
    est_protein_g: int
    score: float


class GroceryItem(BaseModel):
    item: str
    aisle: str
    qty: Optional[str] = None


class PlanResponse(BaseModel):
    recipes: List[RecipeOut]
    grocery_list: List[GroceryItem]
