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
from app.exercises.cloze import INSTRUCTIONS as CLOZE_INSTRUCTIONS
from app.exercises.cloze import generate_cloze
from app.exercises.quiz import INSTRUCTIONS as QUIZ_INSTRUCTIONS
from app.exercises.quiz import generate_quiz
from app.exercises.registry import EXERCISE_TYPES
from app.language import detect_language, is_cjk
from app.models import Base, Exercise, ExerciseAttempt, Text

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


class TextCreate(BaseModel):
    content: str
    ai_provider: str


class AnswerCheck(BaseModel):
    item_index: int
    answer: int | str


class AttemptSubmit(BaseModel):
    answers: list[int | str]


@app.get("/health")
def health() -> dict:
    """Liveness check, used by monitoring and by the CI smoke test."""
    return {"status": "ok", "environment": settings.environment}


@app.get("/ai/providers")
def list_providers() -> dict:
    """Lists AI provider names, used to populate the frontend selector (Phase 6)."""
    return {"providers": available_providers()}


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
    text = _get_text_or_404(text_id, db)
    return {
        "id": text.id,
        "content": text.content,
        "language": text.language,
        "ai_provider": text.ai_provider,
    }


def _get_text_or_404(text_id: int, db: Session) -> Text:
    text = db.query(Text).filter(Text.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    return text


def _get_exercise_or_404(exercise_id: int, db: Session) -> Exercise:
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@app.post("/texts/{text_id}/exercises/quiz")
def create_quiz_exercise(text_id: int, db: Session = Depends(get_db)) -> dict:
    text = _get_text_or_404(text_id, db)
    provider = get_ai_provider(text.ai_provider)

    questions = generate_quiz(text.content, provider)

    exercise = Exercise(
        text_id=text.id,
        type="quiz",
        instructions=QUIZ_INSTRUCTIONS,
        data={"questions": questions},
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)

    # correct_index is stripped from the response so the student can't
    # inspect it in the browser network tab before answering.
    questions_without_answers = [
        {"question": q["question"], "options": q["options"]} for q in questions
    ]

    return {
        "exercise_id": exercise.id,
        "type": "quiz",
        "instructions": exercise.instructions,
        "questions": questions_without_answers,
    }


@app.post("/texts/{text_id}/exercises/cloze")
def create_cloze_exercise(text_id: int, db: Session = Depends(get_db)) -> dict:
    text = _get_text_or_404(text_id, db)
    provider = get_ai_provider(text.ai_provider)

    sentences = generate_cloze(text.content, provider)

    exercise = Exercise(
        text_id=text.id,
        type="cloze",
        instructions=CLOZE_INSTRUCTIONS,
        data={"sentences": sentences},
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)

    # The answer is stripped from the response for the same reason as quiz.
    sentences_without_answers = [{"sentence": s["sentence"], "hint": s["hint"]} for s in sentences]

    return {
        "exercise_id": exercise.id,
        "type": "cloze",
        "instructions": exercise.instructions,
        "sentences": sentences_without_answers,
    }


@app.post("/exercises/{exercise_id}/answer")
def answer_exercise_item(
    exercise_id: int, payload: AnswerCheck, db: Session = Depends(get_db)
) -> dict:
    """Immediate per-item feedback, generic across exercise types: checks a
    single answer and tells the student right away whether it was correct,
    without ending the exercise."""
    exercise = _get_exercise_or_404(exercise_id, db)
    config = EXERCISE_TYPES.get(exercise.type)
    if config is None:
        raise HTTPException(
            status_code=400, detail=f"Exercise type '{exercise.type}' does not support answers"
        )

    items = exercise.data[config["data_key"]]
    if not (0 <= payload.item_index < len(items)):
        raise HTTPException(status_code=400, detail="Invalid item_index")

    return config["check_answer"](items, payload.item_index, payload.answer)


@app.post("/exercises/{exercise_id}/attempt")
def submit_exercise_attempt(
    exercise_id: int, payload: AttemptSubmit, db: Session = Depends(get_db)
) -> dict:
    """Records the full set of answers once the student finishes an
    exercise. This is what feeds the final results chart across all
    exercise types (Phase 5, final step)."""
    exercise = _get_exercise_or_404(exercise_id, db)
    config = EXERCISE_TYPES.get(exercise.type)
    if config is None:
        raise HTTPException(
            status_code=400, detail=f"Exercise type '{exercise.type}' does not support attempts"
        )

    items = exercise.data[config["data_key"]]
    score, total = config["score_attempt"](items, payload.answers)

    attempt = ExerciseAttempt(
        exercise_id=exercise.id, score=score, total=total, answers={"submitted": payload.answers}
    )
    db.add(attempt)
    db.commit()

    return {"score": score, "total": total}
