import json
from abc import ABC, abstractmethod

from app.ai.exceptions import AIGenerationError


class AIProvider(ABC):
    """Common interface every AI provider must implement.

    Exercise-generation code (Phase 5) depends only on this interface, never
    on a specific provider's SDK. This is what makes the provider selectable
    per request without touching business logic.
    """

    name: str

    @abstractmethod
    def is_configured(self) -> bool:
        """Whether the required API key is present."""

    @abstractmethod
    def _generate_raw(self, prompt: str) -> str:
        """Provider-specific call that returns the raw text response."""

    def generate_json(self, prompt: str) -> list | dict:
        """Calls the provider and parses the response as JSON.

        Shared across all providers: strips markdown code fences some models
        add even when instructed not to, and fails loudly on invalid JSON
        instead of silently returning garbage to the caller.
        """
        raw = self._generate_raw(prompt).strip()

        if raw.startswith("```"):
            raw = raw.strip("`").removeprefix("json").strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise AIGenerationError(f"{self.name}: AI response was not valid JSON") from e
