class AIGenerationError(Exception):
    """Raised when an AI provider fails to generate valid content."""


class AIRateLimitError(AIGenerationError):
    """Raised when an AI provider's rate limit / quota has been exceeded."""


class AIProviderNotFoundError(Exception):
    """Raised when an unknown provider name is requested."""


class AIProviderNotConfiguredError(Exception):
    """Raised when a provider is requested but its API key is not set."""
