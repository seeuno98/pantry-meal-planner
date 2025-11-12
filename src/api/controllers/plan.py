from fastapi import APIRouter
from ..schemas import PlanMealsRequest, PlanMealsResponse, RecipeOut

router = APIRouter()


@router.post("/meals", response_model=PlanMealsResponse)
def plan_meals(req: PlanMealsRequest):
    # TODO: wire to rag_service.recommend_recipes(...)
    demo = RecipeOut(
        id="demo-1",
        title="Spicy Tofu Stir-Fry",
        time_minutes=20,
        macros={"kcal": 520, "protein_g": 32},
        pantry_coverage=0.8,
        why="Uses tofu/garlic from your pantry and meets your protein target.",
        missing=["soy sauce"],
    )
    return {
        "recipes": [demo],
        "grocery_list": [{"item": "soy sauce", "qty": "200ml", "aisle": "pantry"}],
    }
