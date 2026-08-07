from app.ai.base import AIProvider
from app.exercises.crossword_layout import crossword_to_dict, generate_crossword

INSTRUCTIONS = (
    "Fill in the crossword grid using the clues provided. Each numbered "
    "clue corresponds to a word placed across or down on the grid."
)

CROSSWORD_WORDS_PROMPT = """Based on the text below, extract 5 to 8 important
words and a short clue for each one, to build a crossword puzzle.

IMPORTANT RULE about the "grid_word" field: it must be a sequence of
characters with NO spaces, suitable for a letter grid where words cross each
other:
- If the text is in Portuguese, English, or another Latin-script language:
  use the word itself (no accents).
- If the text is in Japanese: use the word's reading in HIRAGANA (not kanji),
  since isolated kanji characters don't cross letter-by-letter.
- If the text is in Chinese: use PINYIN with no tone marks, no spaces.

The "original_word" field holds the word as it appears in the text (with
kanji/hanzi if applicable), used as extra context in the clue.

Respond with ONLY valid JSON, no markdown, in this exact format:

[
  {{"grid_word": "...", "original_word": "...", "clue": "..."}}
]

Text:
{text}
"""


def generate_crossword_words(text: str, provider: AIProvider) -> list[dict]:
    """Extracts vocabulary and clues from the text via AI. The grid layout
    itself is built separately by the deterministic algorithm in
    crossword_layout.py."""
    return provider.generate_json(CROSSWORD_WORDS_PROMPT.format(text=text))


def build_crossword_data(words: list[dict]) -> dict:
    """Turns the AI's word/clue list into a placed grid, ready to store in
    Exercise.data."""
    pairs = [(w["grid_word"], f"{w['clue']} ({w['original_word']})") for w in words]
    result = generate_crossword(pairs)
    return crossword_to_dict(result)


def check_answer(words: list[dict], item_index: int, answer: str) -> dict:
    """Checks a single crossword word answer, case-insensitive."""
    item = words[item_index]
    correct_word = item["word"]
    is_correct = str(answer).strip().upper() == correct_word.strip().upper()
    return {
        "correct": is_correct,
        "correct_word": correct_word,
    }


def score_attempt(words: list[dict], answers: list[str]) -> tuple[int, int]:
    """Scores a full attempt (all crossword words) for the final results record."""
    correct = sum(
        1
        for item, given in zip(words, answers, strict=False)
        if str(given).strip().upper() == item["word"].strip().upper()
    )
    return correct, len(words)
