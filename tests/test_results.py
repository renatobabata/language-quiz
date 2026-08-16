from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_QUESTIONS = [
    {"question": "Q1?", "options": ["A", "B", "C", "D"], "correct_index": 0},
]


def _create_text() -> dict:
    return client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque.",
            "ai_provider": "gemini",
        },
    ).json()


def test_results_empty_when_no_exercises_attempted():
    text = _create_text()
    response = client.get(f"/texts/{text['id']}/results")

    assert response.status_code == 200
    body = response.json()
    assert body["exercises"] == []
    assert body["overall_score"] == 0
    assert body["overall_total"] == 0


def test_results_aggregates_attempted_exercises(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "generate_quiz", lambda text, provider: SAMPLE_QUESTIONS)

    text = _create_text()
    exercise = client.post(f"/texts/{text['id']}/exercises/quiz").json()
    client.post(f"/exercises/{exercise['exercise_id']}/attempt", json={"answers": [0]})

    response = client.get(f"/texts/{text['id']}/results")

    assert response.status_code == 200
    body = response.json()
    assert len(body["exercises"]) == 1
    assert body["exercises"][0]["type"] == "quiz"
    assert body["exercises"][0]["score"] == 1
    assert body["overall_score"] == 1
    assert body["overall_total"] == 1


def test_results_skips_exercises_without_any_attempt(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "generate_quiz", lambda text, provider: SAMPLE_QUESTIONS)

    text = _create_text()
    client.post(f"/texts/{text['id']}/exercises/quiz")

    response = client.get(f"/texts/{text['id']}/results")

    assert response.json()["exercises"] == []


def test_results_uses_the_latest_attempt_per_exercise(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "generate_quiz", lambda text, provider: SAMPLE_QUESTIONS)

    text = _create_text()
    exercise = client.post(f"/texts/{text['id']}/exercises/quiz").json()

    client.post(f"/exercises/{exercise['exercise_id']}/attempt", json={"answers": [1]})
    client.post(f"/exercises/{exercise['exercise_id']}/attempt", json={"answers": [0]})

    response = client.get(f"/texts/{text['id']}/results")
    assert response.json()["exercises"][0]["score"] == 1


def test_results_not_found_for_unknown_text():
    response = client.get("/texts/999999/results")
    assert response.status_code == 404
