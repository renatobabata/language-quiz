import logging
import time

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

from app.ai.base import AIProvider
from app.ai.exceptions import AIRateLimitError
from app.config import settings

logger = logging.getLogger(__name__)

# Free tier is rate-limited per minute; retry once instead of failing
# immediately on the first 429.
_MAX_RETRIES = 1
_DEFAULT_RETRY_SECONDS = 20


class GeminiProvider(AIProvider):
    name = "gemini"

    def is_configured(self) -> bool:
        return bool(settings.gemini_api_key)

    def _generate_raw(self, prompt: str) -> str:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)

        attempt = 0
        while True:
            try:
                response = model.generate_content(prompt)
                return response.text
            except ResourceExhausted as e:
                attempt += 1
                wait_seconds = self._extract_retry_delay(e) or _DEFAULT_RETRY_SECONDS
                if attempt > _MAX_RETRIES:
                    raise AIRateLimitError(
                        "Gemini rate limit exceeded. " f"Wait about {wait_seconds}s and try again."
                    ) from e
                logger.warning("Gemini rate limit hit, retrying in %ds...", wait_seconds)
                time.sleep(wait_seconds)

    @staticmethod
    def _extract_retry_delay(error: ResourceExhausted) -> int | None:
        retry_info = getattr(error, "retry_delay", None)
        if retry_info and hasattr(retry_info, "seconds"):
            return retry_info.seconds
        return None
