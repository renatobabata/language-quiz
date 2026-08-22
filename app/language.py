import logging

from langdetect import LangDetectException, detect

logger = logging.getLogger(__name__)

# Languages for which kanji/hanzi flashcard exercises make sense
CJK_LANGUAGES = {"ja", "zh-cn", "zh-tw"}


def detect_language(text: str) -> str:
    """Detects the language of the given text. Returns an ISO code (e.g. 'ja', 'pt', 'en').

    Falls back to 'pt' if detection fails (text too short or ambiguous),
    instead of raising and breaking the request.
    """
    try:
        return detect(text)
    except LangDetectException:
        logger.warning("Could not detect language, falling back to 'pt'")
        return "pt"


def is_cjk(language: str) -> bool:
    """Whether the language supports kanji/hanzi flashcard exercises."""
    return language in CJK_LANGUAGES


def supports_crossword(language: str) -> bool:
    """Chinese text doesn't fit the crossword's letter-by-letter grid model
    the way Japanese (via hiragana readings) or Latin-script languages do,
    so the crossword exercise is disabled specifically for zh-cn/zh-tw."""
    return language not in {"zh-cn", "zh-tw"}
