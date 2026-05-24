import time
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest


app = FastAPI(title="dz8-ml-service", version="1.0.0")

REQUESTS = Counter(
    "requests_total",
    "Total HTTP requests handled by the demo ML service",
    ["endpoint", "method", "status"],
)
PREDICTION_ERRORS = Counter(
    "prediction_errors_total",
    "Total prediction errors in the demo ML service",
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)
MODEL_DRIFT_PSI = Gauge("model_drift_psi", "Latest PSI drift value")
MODEL_DRIFT_PSI.set(0.12)


class PredictRequest(BaseModel):
    features: List[float]
    slow: bool = False


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "dz8-ml-service"}


@app.post("/predict")
def predict(payload: PredictRequest, slow: Optional[bool] = None) -> dict:
    start = time.time()
    status = "200"
    try:
        if not payload.features:
            status = "400"
            PREDICTION_ERRORS.inc()
            raise HTTPException(status_code=400, detail="features must not be empty")

        if payload.slow or bool(slow):
            time.sleep(2)

        score = sum(payload.features) / len(payload.features)
        return {
            "score": round(score, 4),
            "label": int(score > 0.5),
            "model_version": "dz8-demo-v1",
        }
    finally:
        REQUEST_LATENCY.observe(time.time() - start)
        REQUESTS.labels(endpoint="/predict", method="POST", status=status).inc()


@app.post("/alert-webhook")
def alert_webhook(payload: dict | None = None) -> dict:
    return {"status": "received", "payload_keys": sorted((payload or {}).keys())}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
