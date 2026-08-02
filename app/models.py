from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy import Text as SQLText
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Text(Base):
    """A text submitted by the student, pasted into the text box."""

    __tablename__ = "texts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(SQLText)
    language: Mapped[str] = mapped_column(String(10))  # e.g. "ja", "zh-cn", "en", "pt"
    ai_provider: Mapped[str] = mapped_column(String(20))  # "gemini" or "groq"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Exercise(Base):
    """An exercise generated from a text.

    `type` is one of "quiz", "cloze", "flashcard", "crossword".
    `instructions` is the student-facing prompt explaining what to do.
    `data` holds the type-specific structure (shape varies per type, hence JSON).
    """

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text_id: Mapped[int] = mapped_column(ForeignKey("texts.id"))
    type: Mapped[str] = mapped_column(String(20))
    instructions: Mapped[str] = mapped_column(SQLText)
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExerciseAttempt(Base):
    """The student's attempt at a single exercise, used to build the final
    results chart across all exercise types for a given text."""

    __tablename__ = "exercise_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    score: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    answers: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
