from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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


@app.post("/api/metrics")
def get_metrics(request: MetricsRequest):
    return {
        "moi": moi_metric(request),
        "count": len(request.packages),
        "utilization": used_space(request),
        "weight_utilization": used_weight(request),
    }
