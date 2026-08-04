from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.exercises.cloze import check_answer, generate_cloze, score_attempt
from app.main import app

client = TestClient(app)

SAMPLE_SENTENCES = [
    {"sentence": "The cat climbed onto the ___.", "hint": "Where you sleep", "answer": "bed"},
    {"sentence": "She drank a cup of ___.", "hint": "A hot morning drink", "answer": "coffee"},
    {"sentence": "The ___ is shining today.", "hint": "It's in the sky", "answer": "sun"},
    {"sentence": "He read the ___ every day.", "hint": "Printed daily news", "answer": "newspaper"},
    {"sentence": "They live in a small ___.", "hint": "A place with houses", "answer": "town"},
]


def test_generate_cloze_calls_provider_and_returns_sentences():
    mock_provider = MagicMock()
    mock_provider.generate_json.return_value = SAMPLE_SENTENCES

    result = generate_cloze("some text", mock_provider)

    assert result == SAMPLE_SENTENCES
    mock_provider.generate_json.assert_called_once()


def test_check_answer_correct_case_insensitive():
    result = check_answer(SAMPLE_SENTENCES, item_index=0, answer="BED")
    assert result == {"correct": True, "correct_answer": "bed"}


def test_check_answer_incorrect():
    result = check_answer(SAMPLE_SENTENCES, item_index=0, answer="chair")
    assert result == {"correct": False, "correct_answer": "bed"}


def test_check_answer_ignores_surrounding_whitespace():
    result = check_answer(SAMPLE_SENTENCES, item_index=1, answer="  coffee  ")
    assert result["correct"] is True


def test_score_attempt_counts_correct_answers():
    answers = ["bed", "coffee", "moon", "newspaper", "town"]  # 4 correct, "moon" wrong
    score, total = score_attempt(SAMPLE_SENTENCES, answers)
    assert score == 4
    assert total == 5


def test_create_cloze_exercise_endpoint(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "generate_cloze", lambda text, provider: SAMPLE_SENTENCES)

    created_text = client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque.",
            "ai_provider": "gemini",
        },
    ).json()

    response = client.post(f"/texts/{created_text['id']}/exercises/cloze")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "cloze"
    assert len(body["sentences"]) == 5
    # The answer must never be exposed to the client before answering
    assert "answer" not in body["sentences"][0]


def test_cloze_answer_and_attempt_flow(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "generate_cloze", lambda text, provider: SAMPLE_SENTENCES)

    created_text = client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque.",
            "ai_provider": "gemini",
        },
    ).json()
    exercise = client.post(f"/texts/{created_text['id']}/exercises/cloze").json()
    exercise_id = exercise["exercise_id"]

    answer_response = client.post(
        f"/exercises/{exercise_id}/answer",
        json={"item_index": 0, "answer": "bed"},
    )
    assert answer_response.status_code == 200
    assert answer_response.json()["correct"] is True

    attempt_response = client.post(
        f"/exercises/{exercise_id}/attempt",
        json={"answers": ["bed", "coffee", "sun", "newspaper", "town"]},
    )
    assert attempt_response.status_code == 200
    assert attempt_response.json() == {"score": 5, "total": 5}
