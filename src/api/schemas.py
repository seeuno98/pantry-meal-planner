from pydantic import BaseModel
from typing import List, Optional, Dict

class Targets(BaseModel):
    protein_g_min: Optional[float] = None
    kcal_max: Optional[float] = None

class PlanMealsRequest(BaseModel):
    pantry: List[str]
    targets: Optional[Targets] = None
    days: int = 3
    servings: int = 2
    avoid: List[str] = []
    prefer: List[str] = []

class RecipeOut(BaseModel):
    id: str
    title: str
    time_minutes: int
    macros: Dict[str, float]
    pantry_coverage: float
    why: str
    missing: List[str]

class PlanMealsResponse(BaseModel):
    recipes: List[RecipeOut]
    grocery_list: List[Dict[str, str]]
