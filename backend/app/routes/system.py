from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["system"])


@router.get("/")
def home():
    return {
        "service": "Flowmind API",
        "version": "1.0",
        "status": "running",
        "environment": "dev",
    }


@router.get("/health")
def health():
    return {"status": "ok"}
