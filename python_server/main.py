import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware

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


@app.on_event("startup")
def on_startup():
    """Ensure database tables are created on startup."""
    with DatabaseHandler() as db:
        SQLModel.metadata.create_all(db.engine)


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
        requests = db.get_all_requests()
        return [
            {"id": req.id, "timestamp": req.timestamp, "status": req.status}
            for req in requests
        ]


class PostAPIRequest(BaseModel):
    id: int


@app.post("/api/request")
def get_request_result(request: PostAPIRequest):
    with DatabaseHandler() as db:
        response = db.get_response(request.id)
        if response is None:
            raise HTTPException(
                status_code=301,
                detail="There is no item with the provided ID or the request is still being processed.",
            )
        return response


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
