import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.exceptions import (
    AIGenerationError,
    AIProviderNotConfiguredError,
    AIProviderNotFoundError,
    AIRateLimitError,
)
from app.ai.factory import available_providers, get_ai_provider
from app.config import settings
from app.database import engine, get_db
from app.language import detect_language, is_cjk
from app.models import Base, Text

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="Language Quiz", version="0.1.0")

# A real migration tool (Alembic) would replace this once the schema
# stabilizes; fine for now while the data model is still evolving.
Base.metadata.create_all(bind=engine)


@app.exception_handler(AIRateLimitError)
async def rate_limit_handler(request: Request, exc: AIRateLimitError) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": str(exc)})


@app.exception_handler(AIGenerationError)
async def ai_generation_error_handler(request: Request, exc: AIGenerationError) -> JSONResponse:
    logger.error("AI generation error: %s", exc)
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(AIProviderNotFoundError)
async def provider_not_found_handler(
    request: Request, exc: AIProviderNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(AIProviderNotConfiguredError)
async def provider_not_configured_handler(
    request: Request, exc: AIProviderNotConfiguredError
) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


class AIPingRequest(BaseModel):
    provider: str
    prompt: str = 'Reply with a short JSON object: {"status": "ok"}'


class TextCreate(BaseModel):
    content: str
    ai_provider: str


@app.get("/health")
def health() -> dict:
    """Liveness check, used by monitoring and by the CI smoke test."""
    return {"status": "ok", "environment": settings.environment}


@app.get("/ai/providers")
def list_providers() -> dict:
    """Lists AI provider names, used to populate the frontend selector (Phase 6)."""
    return {"providers": available_providers()}


@app.post("/ai/ping")
def ai_ping(payload: AIPingRequest) -> dict:
    """Temporary manual-testing endpoint for the AI abstraction layer.

    Will be removed once the real exercise-generation endpoints exist.
    """
    provider = get_ai_provider(payload.provider)
    result = provider.generate_json(payload.prompt)
    return {"provider": provider.name, "result": result}


@app.post("/texts")
def create_text(payload: TextCreate, db: Session = Depends(get_db)) -> dict:
    """Submits a text for study. Validates the chosen AI provider up front
    (fails fast, before anything is generated) and detects the language."""
    if not payload.content or len(payload.content.strip()) < 20:
        raise HTTPException(status_code=400, detail="Text is too short (minimum 20 characters)")

    # Validates the provider exists and is configured; raises the
    # appropriate handled exception otherwise (400 or 503).
    get_ai_provider(payload.ai_provider)

    language = detect_language(payload.content)
    text = Text(content=payload.content, language=language, ai_provider=payload.ai_provider)
    db.add(text)
    db.commit()
    db.refresh(text)

    return {
        "id": text.id,
        "language": text.language,
        "ai_provider": text.ai_provider,
        "supports_kanji_flashcards": is_cjk(text.language),
    }


@app.get("/texts/{text_id}")
def get_text(text_id: int, db: Session = Depends(get_db)) -> dict:
    text = db.query(Text).filter(Text.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    return {
        "id": text.id,
        "content": text.content,
        "language": text.language,
        "ai_provider": text.ai_provider,
    }
