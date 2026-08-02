from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings


def _ensure_sqlite_dir_exists(database_url: str) -> None:
    """Ensures the SQLite file's parent directory exists before connecting.

    Without this, SQLAlchemy fails with 'unable to open database file' on
    any fresh environment (CI, a newly created VM) where the folder hasn't
    been created manually yet.
    """
    if not database_url.startswith("sqlite:///"):
        return
    db_path = database_url.removeprefix("sqlite:///")
    if db_path == ":memory:":
        return
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_dir_exists(settings.database_url)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: opens a DB session and guarantees it's closed
    even if the request raises."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
