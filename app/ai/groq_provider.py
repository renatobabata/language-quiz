import logging

from groq import APIStatusError, Groq

from app.ai.base import AIProvider
from app.ai.exceptions import AIGenerationError, AIRateLimitError
from app.config import settings

logger = logging.getLogger(__name__)


class GroqProvider(AIProvider):
    name = "groq"

    def is_configured(self) -> bool:
        return bool(settings.groq_api_key)

    def _generate_raw(self, prompt: str) -> str:
        client = Groq(api_key=settings.groq_api_key)

        try:
            response = client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except APIStatusError as e:
            if e.status_code == 429:
                raise AIRateLimitError(
                    "Groq rate limit exceeded. Wait a moment and try again."
                ) from e
            logger.error("Groq API error (status %s): %s", e.status_code, e)
            raise AIGenerationError(f"Groq API error: {e}") from e
