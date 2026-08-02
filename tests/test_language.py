from app.language import detect_language, is_cjk


def test_detect_language_japanese():
    assert detect_language("今日はいい天気ですね。散歩に行きましょう。") == "ja"


def test_detect_language_portuguese():
    assert detect_language("Hoje esta um dia muito bonito para passear no parque.") == "pt"


def test_is_cjk_true_for_japanese():
    assert is_cjk("ja") is True


def test_is_cjk_false_for_portuguese():
    assert is_cjk("pt") is False


def test_detect_language_fallback_on_empty_text():
    assert detect_language("") == "pt"
