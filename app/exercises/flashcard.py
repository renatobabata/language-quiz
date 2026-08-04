from app.ai.base import AIProvider
from app.language import is_cjk

READING_INSTRUCTIONS = (
    "For each flashcard, choose the correct reading of the highlighted word "
    "among the four options."
)

SYNONYM_INSTRUCTIONS = (
    "For each flashcard, choose the word among the four options that has "
    "the same meaning (synonym) as the one shown."
)

READING_PROMPT = """Based on the text below, extract 5 key words written in
kanji/hanzi. For each one, provide the word itself and 4 reading options in
{reading_script} — one correct, and three plausible but incorrect readings
(not random characters; they should look like real, believable alternatives
a learner might confuse it with). Respond with ONLY valid JSON, no markdown,
in this exact format:

[
  {{"word": "...", "options": ["...", "...", "...", "..."], "correct_index": 0}}
]

Text:
{text}
"""

SYNONYM_PROMPT = """Based on the text below, extract 5 key words. For each
one, provide the word itself and 4 option words in the SAME language as the
text — one of them a true synonym (same meaning), and three plausible
distractors (different meaning, but same part of speech/register, not
obviously wrong). Respond with ONLY valid JSON, no markdown, in this exact
format:

[
  {{"word": "...", "options": ["...", "...", "...", "..."], "correct_index": 0}}
]

Text:
{text}
"""


def generate_flashcards(text: str, provider: AIProvider, language: str) -> list[dict]:
    """Generates 5 flashcards. For Japanese/Chinese texts, the exercise is
    choosing the correct hiragana/pinyin reading; for other languages, it's
    choosing the correct synonym."""
    if is_cjk(language):
        reading_script = "hiragana" if language == "ja" else "pinyin (no tone marks)"
        prompt = READING_PROMPT.format(text=text, reading_script=reading_script)
    else:
        prompt = SYNONYM_PROMPT.format(text=text)

    return provider.generate_json(prompt)


def get_instructions(language: str) -> str:
    return READING_INSTRUCTIONS if is_cjk(language) else SYNONYM_INSTRUCTIONS
