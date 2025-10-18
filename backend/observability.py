import time
import uuid
import logging
import sys
from fastapi import FastAPI, Request
from starlette.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware

REQS = Counter("http_requests_total", "HTTP requests", ["path", "method", "status"])
LAT = Histogram(
    "http_request_duration_seconds", "HTTP request duration", ["path", "method"]
)

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    # Basic JSON-like format without additional dependency
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
    )
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = []
    root.setLevel(logging.INFO)
    root.addHandler(handler)

def setup_cors(app: FastAPI, origins: list[str]):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

def setup_rate_limit(app: FastAPI, rate: str) -> Limiter:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter

    @app.middleware("http")
    async def rl_mw(request: Request, call_next):
        return await call_next(request)

    return limiter

def wire(app: FastAPI):
    setup_logging()

    @app.middleware("http")
    async def metrics_mw(request: Request, call_next):
        rid = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            dur = time.perf_counter() - start
            path = request.url.path
            method = request.method
            status = response.status_code if response else 500
            REQS.labels(path, method, status).inc()
            LAT.labels(path, method).observe(dur)
            logging.getLogger("app").info(
                f'{{"msg":"req","rid":"{rid}","path":"{path}","method":"{method}","status":{status},"duration":{round(dur,3)}}}'
            )

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    @app.get("/readiness")
    def readiness():
        return {"ready": True}

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
