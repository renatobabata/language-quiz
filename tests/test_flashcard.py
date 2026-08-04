from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.exercises.flashcard import generate_flashcards, get_instructions
from app.main import app

client = TestClient(app)

SAMPLE_READING_CARDS = [
    {"word": "猫", "options": ["ねこ", "いぬ", "とり", "うま"], "correct_index": 0},
]

SAMPLE_SYNONYM_CARDS = [
    {"word": "happy", "options": ["joyful", "car", "table", "run"], "correct_index": 0},
]


def test_generate_flashcards_uses_reading_prompt_for_japanese():
    mock_provider = MagicMock()
    mock_provider.generate_json.return_value = SAMPLE_READING_CARDS

    result = generate_flashcards("猫が好きです", mock_provider, "ja")

    assert result == SAMPLE_READING_CARDS
    prompt_used = mock_provider.generate_json.call_args[0][0]
    assert "hiragana" in prompt_used


def test_generate_flashcards_uses_pinyin_prompt_for_chinese():
    mock_provider = MagicMock()
    mock_provider.generate_json.return_value = SAMPLE_READING_CARDS

    generate_flashcards("你好世界", mock_provider, "zh-cn")

    prompt_used = mock_provider.generate_json.call_args[0][0]
    assert "pinyin" in prompt_used


def test_generate_flashcards_uses_synonym_prompt_for_other_languages():
    mock_provider = MagicMock()
    mock_provider.generate_json.return_value = SAMPLE_SYNONYM_CARDS

    generate_flashcards("some english text here", mock_provider, "en")

    prompt_used = mock_provider.generate_json.call_args[0][0]
    assert "synonym" in prompt_used


def test_get_instructions_differs_by_language():
    assert get_instructions("ja") != get_instructions("en")
    assert get_instructions("zh-cn") == get_instructions("ja")


def test_create_flashcard_exercise_endpoint_japanese(monkeypatch):
    from app import main

    monkeypatch.setattr(
        main, "generate_flashcards", lambda text, provider, language: SAMPLE_READING_CARDS
    )

    created_text = client.post(
        "/texts",
        json={
            "content": "今日はいい天気ですね。散歩に行きましょう。桜の花が咲いています。",
            "ai_provider": "gemini",
        },
    ).json()

    response = client.post(f"/texts/{created_text['id']}/exercises/flashcards")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "flashcard"
    assert "correct_index" not in body["cards"][0]


def test_flashcard_answer_and_attempt_flow(monkeypatch):
    from app import main

    monkeypatch.setattr(
        main, "generate_flashcards", lambda text, provider, language: SAMPLE_READING_CARDS
    )

    created_text = client.post(
        "/texts",
        json={
            "content": "今日はいい天気ですね。散歩に行きましょう。桜の花が咲いています。",
            "ai_provider": "gemini",
        },
    ).json()
    exercise = client.post(f"/texts/{created_text['id']}/exercises/flashcards").json()
    exercise_id = exercise["exercise_id"]

    answer_response = client.post(
        f"/exercises/{exercise_id}/answer",
        json={"item_index": 0, "answer": 0},
    )
    assert answer_response.status_code == 200
    assert answer_response.json()["correct"] is True

    attempt_response = client.post(
        f"/exercises/{exercise_id}/attempt",
        json={"answers": [0]},
    )
    assert attempt_response.status_code == 200
    assert attempt_response.json() == {"score": 1, "total": 1}
