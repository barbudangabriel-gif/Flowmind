"""
Observability layer: health, metrics, structured logs, request correlation
"""

import time
import uuid
import logging
import json
from typing import Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Prometheus metrics
REQUESTS_TOTAL = Counter(
    "http_requests_total", "Total HTTP requests", ["path", "method", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["path", "method"]
)

# Structured logger
logger = logging.getLogger("flowmind")


class StructuredLogger:
    """Structured JSON logger for better observability"""

    @staticmethod
    def info(data: Dict[str, Any]):
        logger.info(json.dumps(data))

    @staticmethod
    def error(data: Dict[str, Any]):
        logger.error(json.dumps(data))

    @staticmethod
    def warning(data: Dict[str, Any]):
        logger.warning(json.dumps(data))


slog = StructuredLogger()


def wire_observability(app: FastAPI):
    """Wire observability into FastAPI app"""

    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        # Generate request ID for correlation
        request_id = request.headers.get("x-request-id", str(uuid.uuid4())[:8])

        # Start timing
        start_time = time.perf_counter()

        # Process request
        response = None
        status_code = 500  # Default for exceptions

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response

        except Exception as e:
            # Log unexpected errors
            slog.error(
                {
                    "event": "request_error",
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )

            # Return 500 error
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "request_id": request_id},
            )

        finally:
            # Calculate duration
            duration = time.perf_counter() - start_time

            # Update metrics
            path = request.url.path
            method = request.method
            REQUESTS_TOTAL.labels(path=path, method=method, status=status_code).inc()
            REQUEST_DURATION.labels(path=path, method=method).observe(duration)

            # Structured logging
            slog.info(
                {
                    "event": "request_completed",
                    "request_id": request_id,
                    "path": path,
                    "method": method,
                    "status": status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "user_agent": request.headers.get("user-agent", ""),
                }
            )

            # Add request ID to response headers
            if response:
                response.headers["x-request-id"] = request_id

    @app.get("/healthz")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "flowmind-backend",
        }

    @app.get("/metrics")
    async def prometheus_metrics():
        """Prometheus metrics endpoint"""
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/readiness")
    async def readiness_check():
        """Readiness check - can include dependency checks"""
        # TODO[OPS-009]: Add database connectivity check
        # TODO[OPS-010]: Add external API health checks
        return {
            "status": "ready",
            "timestamp": time.time(),
            "checks": {
                "database": "not_implemented",
                "external_apis": "not_implemented",
            },
        }


# Configure structured logging format
def configure_logging():
    """Configure structured logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
