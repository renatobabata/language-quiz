from app.ai.base import AIProvider
from app.ai.exceptions import AIProviderNotConfiguredError, AIProviderNotFoundError
from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider

_PROVIDERS: dict[str, type[AIProvider]] = {
    "gemini": GeminiProvider,
    "groq": GroqProvider,
}


def available_providers() -> list[str]:
    """Provider names, used to populate the frontend selector."""
    return list(_PROVIDERS.keys())


def get_ai_provider(name: str) -> AIProvider:
    """Returns a configured provider instance by name.

    This is the only place exercise-generation code should call to obtain a
    provider — never instantiate GeminiProvider/GroqProvider directly.
    """
    provider_cls = _PROVIDERS.get(name)
    if provider_cls is None:
        raise AIProviderNotFoundError(
            f"Unknown AI provider '{name}'. Available: {', '.join(_PROVIDERS)}"
        )

    provider = provider_cls()
    if not provider.is_configured():
        raise AIProviderNotConfiguredError(f"Provider '{name}' is not configured (missing API key)")
    return provider
