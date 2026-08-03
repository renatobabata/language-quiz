from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_text_returns_detected_language():
    response = client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque com o cachorro.",
            "ai_provider": "gemini",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "pt"
    assert body["ai_provider"] == "gemini"
    assert body["supports_kanji_flashcards"] is False


def test_create_text_detects_japanese_and_flags_kanji_support():
    response = client.post(
        "/texts",
        json={
            "content": "今日はいい天気ですね。散歩に行きましょう。桜の花が咲いています。",
            "ai_provider": "groq",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "ja"
    assert body["supports_kanji_flashcards"] is True


def test_create_text_rejects_too_short_content():
    response = client.post("/texts", json={"content": "short", "ai_provider": "gemini"})
    assert response.status_code == 400


def test_create_text_rejects_unknown_provider():
    response = client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque.",
            "ai_provider": "chatgpt",
        },
    )
    assert response.status_code == 400


def test_get_text_not_found():
    response = client.get("/texts/999999")
    assert response.status_code == 404


def test_get_text_returns_saved_content():
    created = client.post(
        "/texts",
        json={
            "content": "Hoje esta um dia muito bonito para passear no parque.",
            "ai_provider": "gemini",
        },
    ).json()

    response = client.get(f"/texts/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
