from fastapi.testclient import TestClient

from app.exercises.crossword import build_crossword_data, check_answer, score_attempt
from app.exercises.crossword_layout import crossword_to_dict, generate_crossword
from app.main import app

client = TestClient(app)

SAMPLE_WORDS = [
    {"grid_word": "GATO", "original_word": "gato", "clue": "domestic animal"},
    {"grid_word": "TATO", "original_word": "tato", "clue": "one of the senses"},
]


def test_generate_crossword_places_all_words():
    result = generate_crossword([("GATO", "clue 1"), ("SOL", "clue 2")])
    assert len(result.words) == 2
    assert {w.word for w in result.words} == {"GATO", "SOL"}


def test_generate_crossword_empty_list_returns_empty_result():
    result = generate_crossword([])
    assert result.words == []
    assert result.height == 0
    assert result.width == 0


def test_crossword_to_dict_serializes_correctly():
    result = generate_crossword([("SOL", "sun")])
    data = crossword_to_dict(result)
    assert data["words"][0]["word"] == "SOL"
    assert "row" in data["words"][0]


def test_build_crossword_data_from_ai_word_list():
    data = build_crossword_data(SAMPLE_WORDS)
    words = {w["word"] for w in data["words"]}
    assert words == {"GATO", "TATO"}


def test_check_answer_correct_case_insensitive():
    words = [{"word": "GATO", "clue": "c", "row": 0, "col": 0, "direction": "across", "number": 1}]
    result = check_answer(words, 0, "gato")
    assert result == {"correct": True, "correct_word": "GATO"}


def test_check_answer_incorrect():
    words = [{"word": "GATO", "clue": "c", "row": 0, "col": 0, "direction": "across", "number": 1}]
    result = check_answer(words, 0, "cachorro")
    assert result["correct"] is False


def test_score_attempt_counts_correct():
    words = [
        {"word": "GATO", "clue": "c", "row": 0, "col": 0, "direction": "across", "number": 1},
        {"word": "SOL", "clue": "c", "row": 1, "col": 0, "direction": "across", "number": 2},
    ]
    score, total = score_attempt(words, ["gato", "lua"])
    assert score == 1
    assert total == 2


def test_create_crossword_exercise_endpoint(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "generate_crossword_words", lambda text, provider: SAMPLE_WORDS)

    created_text = client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque.",
            "ai_provider": "gemini",
        },
    ).json()

    response = client.post(f"/texts/{created_text['id']}/exercises/crossword")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "crossword"
    # the answer word itself must never be exposed before answering
    assert "word" not in body["words"][0]
    assert "length" in body["words"][0]


def test_crossword_answer_and_attempt_flow(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "generate_crossword_words", lambda text, provider: SAMPLE_WORDS)

    created_text = client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque.",
            "ai_provider": "gemini",
        },
    ).json()
    exercise = client.post(f"/texts/{created_text['id']}/exercises/crossword").json()
    exercise_id = exercise["exercise_id"]

    answer_response = client.post(
        f"/exercises/{exercise_id}/answer",
        json={"item_index": 0, "answer": "gato"},
    )
    assert answer_response.status_code == 200
    assert "correct" in answer_response.json()

    attempt_response = client.post(
        f"/exercises/{exercise_id}/attempt",
        json={"answers": ["gato", "tato"]},
    )
    assert attempt_response.status_code == 200
    assert attempt_response.json()["total"] == 2


def test_create_crossword_exercise_rejects_chinese_text():
    created_text = client.post(
        "/texts",
        json={
            "content": "你好，今天天气很好，我们去公园散步吧。晚上我们一起吃饭吧.",
            "ai_provider": "gemini",
        },
    ).json()

    response = client.post(f"/texts/{created_text['id']}/exercises/crossword")

    assert response.status_code == 400
