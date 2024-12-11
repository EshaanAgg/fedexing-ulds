import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from solution import generate_solution, Request as SolutionRequest
from metrics_handler import (
    moi_metric,
    Request as MetricsRequest,
    used_space,
    used_weight,
    stability,
    pack_volume,
)
from utils import get_class_hash
from database import DatabaseHandler

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
    hash = get_class_hash(request)

    with DatabaseHandler() as db:
        # If the request has already been processed, return the result
        already_processed, result = db.get_request(hash)
        if already_processed:
            return {
                "status": "processed",
                "result": result,
            }

        request_id = db.add_new_request(hash)

    # Start a new thread to process the request and return the result immediately
    thread = threading.Thread(
        target=generate_solution,
        args=(request, request_id),
    )
    thread.start()

    return {"status": "processing", "request_id": request_id}


@app.get("/api/requests")
def get_requests():
    with DatabaseHandler() as db:
        return db.get_all_requests()


class Post_API_Request(BaseModel):
    id: int


@app.post("/api/request")
def get_request_result(request: Post_API_Request):
    with DatabaseHandler() as db:
        return db.get_reponse(request.id)


@app.post("/api/metrics")
def get_metrics(request: MetricsRequest):
    return {
        "moi": moi_metric(request),
        "count": len(request.packages),
        "utilization": used_space(request),
        "weight_utilization": used_weight(request),
        "stability": stability(request),
        "pack_volume": pack_volume(request),
    }
