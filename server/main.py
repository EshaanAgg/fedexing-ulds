from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from solution import generate_solution, Request as SolutionRequest
from metrics_handler import (
    moi_metric,
    Request as MetricsRequest,
    used_space,
    used_weight,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/api")
def get_solution(request: SolutionRequest):
    return generate_solution(request)


@app.post("/api/metrics")
def get_metrics(request: MetricsRequest):
    return {
        "moi": moi_metric(request),
        "count": len(request.packages),
        "utilization": used_space(request),
        "weight_utilization": used_weight(request),
    }
