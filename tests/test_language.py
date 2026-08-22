from app.language import detect_language, is_cjk, supports_crossword


def test_detect_language_japanese():
    assert detect_language("今日はいい天気ですね。散歩に行きましょう。") == "ja"


def test_detect_language_chinese():
    assert detect_language("你好，今天天气很好，我们去公园散步吧。") in {"zh-cn", "zh-tw"}


def test_detect_language_portuguese():
    assert detect_language("Hoje esta um dia muito bonito para passear no parque.") == "pt"


def test_is_cjk_true_for_japanese():
    assert is_cjk("ja") is True


def test_is_cjk_true_for_chinese():
    assert is_cjk("zh-cn") is True
    assert is_cjk("zh-tw") is True


def test_is_cjk_false_for_portuguese():
    assert is_cjk("pt") is False


def test_detect_language_fallback_on_empty_text():
    assert detect_language("") == "pt"


def test_supports_crossword_false_for_chinese():
    assert supports_crossword("zh-cn") is False
    assert supports_crossword("zh-tw") is False


def test_supports_crossword_true_for_japanese():
    # Japanese crosswords work via hiragana readings, unlike Chinese
    assert supports_crossword("ja") is True


def test_supports_crossword_true_for_other_languages():
    assert supports_crossword("pt") is True
    assert supports_crossword("en") is True
