import logging

from fastapi import FastAPI

from app.config import settings

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="Language Quiz", version="0.1.0")


@app.get("/health")
def health() -> dict:
    """Liveness check, used by monitoring and by the CI smoke test."""
    return {"status": "ok", "environment": settings.environment}
