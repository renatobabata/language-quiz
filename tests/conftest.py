import os

# This file is loaded by pytest before any test module is collected/imported,
# which matters because app.config.settings is a module-level singleton
# instantiated on first import. If a test file imported the app before these
# variables were set, `settings` would be locked in with empty API keys for
# the rest of the test session — regardless of what a later test file sets.
os.environ.setdefault("GEMINI_API_KEY", "test-key-fake")
os.environ.setdefault("GROQ_API_KEY", "test-key-fake")
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/test.db")
