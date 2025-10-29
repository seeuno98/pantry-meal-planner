from fastapi import FastAPI
from .controllers import plan, health
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

app = FastAPI(title="Pantry Meal Planner")
app.include_router(health.router, prefix="/health")
app.include_router(plan.router, prefix="/plan")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
