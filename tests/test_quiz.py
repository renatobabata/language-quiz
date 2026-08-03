from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.exercises.quiz import check_answer, generate_quiz, score_attempt
from app.main import app

client = TestClient(app)

SAMPLE_QUESTIONS = [
    {"question": "Q1?", "options": ["A", "B", "C", "D"], "correct_index": 0},
    {"question": "Q2?", "options": ["A", "B", "C", "D"], "correct_index": 1},
    {"question": "Q3?", "options": ["A", "B", "C", "D"], "correct_index": 2},
    {"question": "Q4?", "options": ["A", "B", "C", "D"], "correct_index": 3},
    {"question": "Q5?", "options": ["A", "B", "C", "D"], "correct_index": 0},
]


def test_generate_quiz_calls_provider_and_returns_questions():
    mock_provider = MagicMock()
    mock_provider.generate_json.return_value = SAMPLE_QUESTIONS

    result = generate_quiz("some text", mock_provider)

    assert result == SAMPLE_QUESTIONS
    mock_provider.generate_json.assert_called_once()


def test_check_answer_correct():
    result = check_answer(SAMPLE_QUESTIONS, question_index=0, answer_index=0)
    assert result == {"correct": True, "correct_index": 0}


def test_check_answer_incorrect():
    result = check_answer(SAMPLE_QUESTIONS, question_index=0, answer_index=1)
    assert result == {"correct": False, "correct_index": 0}


def test_score_attempt_counts_correct_answers():
    answers = [0, 1, 0, 3, 0]  # 4 correct out of 5 (question 3 wrong: 0 != 2)
    score, total = score_attempt(SAMPLE_QUESTIONS, answers)
    assert score == 4
    assert total == 5


def test_create_quiz_exercise_endpoint(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "generate_quiz", lambda text, provider: SAMPLE_QUESTIONS)

    created_text = client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque.",
            "ai_provider": "gemini",
        },
    ).json()

    response = client.post(f"/texts/{created_text['id']}/exercises/quiz")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "quiz"
    assert len(body["questions"]) == 5
    # correct_index must never be exposed to the client before answering
    assert "correct_index" not in body["questions"][0]


def test_quiz_answer_and_attempt_flow(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "generate_quiz", lambda text, provider: SAMPLE_QUESTIONS)

    created_text = client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque.",
            "ai_provider": "gemini",
        },
    ).json()
    exercise = client.post(f"/texts/{created_text['id']}/exercises/quiz").json()
    exercise_id = exercise["exercise_id"]

    # Immediate per-question feedback
    answer_response = client.post(
        f"/exercises/{exercise_id}/answer",
        json={"question_index": 0, "answer_index": 0},
    )
    assert answer_response.status_code == 200
    assert answer_response.json()["correct"] is True

    # Final attempt, all 5 answers submitted together
    attempt_response = client.post(
        f"/exercises/{exercise_id}/attempt",
        json={"answers": [0, 1, 2, 3, 0]},
    )
    assert attempt_response.status_code == 200
    assert attempt_response.json() == {"score": 5, "total": 5}


def test_answer_invalid_question_index_returns_400(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "generate_quiz", lambda text, provider: SAMPLE_QUESTIONS)

    created_text = client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque.",
            "ai_provider": "gemini",
        },
    ).json()
    exercise = client.post(f"/texts/{created_text['id']}/exercises/quiz").json()

    response = client.post(
        f"/exercises/{exercise['exercise_id']}/answer",
        json={"question_index": 99, "answer_index": 0},
    )
    assert response.status_code == 400
