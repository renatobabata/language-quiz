from unittest.mock import MagicMock, patch

import pytest

from app.ai.exceptions import (
    AIGenerationError,
    AIProviderNotConfiguredError,
    AIProviderNotFoundError,
)
from app.ai.factory import available_providers, get_ai_provider
from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider


def test_available_providers_lists_both():
    assert set(available_providers()) == {"gemini", "groq"}


def test_get_ai_provider_unknown_name_raises():
    with pytest.raises(AIProviderNotFoundError):
        get_ai_provider("chatgpt")


def test_get_ai_provider_not_configured_raises():
    with patch.object(GeminiProvider, "is_configured", return_value=False):
        with pytest.raises(AIProviderNotConfiguredError):
            get_ai_provider("gemini")


@patch("app.ai.gemini_provider.genai")
@patch("app.ai.gemini_provider.settings")
def test_gemini_generate_json_parses_valid_json(mock_settings, mock_genai):
    mock_settings.gemini_api_key = "fake-key"
    mock_settings.gemini_model = "gemini-3.5-flash"
    mock_response = MagicMock()
    mock_response.text = '{"status": "ok"}'
    mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response

    provider = GeminiProvider()
    result = provider.generate_json("test prompt")

    assert result == {"status": "ok"}


@patch("app.ai.gemini_provider.genai")
@patch("app.ai.gemini_provider.settings")
def test_gemini_strips_markdown_fences(mock_settings, mock_genai):
    mock_settings.gemini_api_key = "fake-key"
    mock_settings.gemini_model = "gemini-3.5-flash"
    mock_response = MagicMock()
    mock_response.text = '```json\n{"status": "ok"}\n```'
    mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response

    provider = GeminiProvider()
    result = provider.generate_json("test prompt")

    assert result == {"status": "ok"}


@patch("app.ai.groq_provider.Groq")
@patch("app.ai.groq_provider.settings")
def test_groq_generate_json_parses_valid_json(mock_settings, mock_groq_cls):
    mock_settings.groq_api_key = "fake-key"
    mock_settings.groq_model = "llama-3.3-70b-versatile"

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '{"status": "ok"}'
    mock_client.chat.completions.create.return_value.choices = [mock_choice]
    mock_groq_cls.return_value = mock_client

    provider = GroqProvider()
    result = provider.generate_json("test prompt")

    assert result == {"status": "ok"}


@patch("app.ai.gemini_provider.genai")
@patch("app.ai.gemini_provider.settings")
def test_generate_json_raises_on_invalid_json(mock_settings, mock_genai):
    mock_settings.gemini_api_key = "fake-key"
    mock_settings.gemini_model = "gemini-3.5-flash"
    mock_response = MagicMock()
    mock_response.text = "this is not json"
    mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response

    provider = GeminiProvider()
    with pytest.raises(AIGenerationError):
        provider.generate_json("test prompt")
