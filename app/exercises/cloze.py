from app.ai.base import AIProvider

INSTRUCTIONS = (
    "Read each sentence taken from the text and fill in the blank with the "
    "missing word. A hint is provided for each one, but it won't give the "
    "exact answer away."
)

CLOZE_PROMPT = """Based on the text below, select 5 important sentences and
remove ONE key word from each (replace it with "___"). For each one, provide
a short hint in the SAME language as the text that helps the student guess
the word WITHOUT giving it away directly — the hint must not contain the
missing word itself, an obvious synonym, or a direct translation of it.
Respond with ONLY valid JSON, no markdown, in this exact format:

[
  {{"sentence": "The cat climbed onto the ___.", "hint": "Where you sleep at night",
    "answer": "bed"}}
]

Text:
{text}
"""


def generate_cloze(text: str, provider: AIProvider) -> list[dict]:
    """Generates 5 fill-in-the-blank sentences from the given text."""
    return provider.generate_json(CLOZE_PROMPT.format(text=text))


def check_answer(sentences: list[dict], item_index: int, answer: str) -> dict:
    """Checks a single fill-in-the-blank answer, case- and whitespace-insensitive."""
    item = sentences[item_index]
    correct_answer = item["answer"]
    is_correct = str(answer).strip().lower() == correct_answer.strip().lower()
    return {
        "correct": is_correct,
        "correct_answer": correct_answer,
    }


def score_attempt(sentences: list[dict], answers: list[str]) -> tuple[int, int]:
    """Scores a full attempt (all 5 answers) for the final results record."""
    correct = sum(
        1
        for item, given in zip(sentences, answers, strict=False)
        if str(given).strip().lower() == item["answer"].strip().lower()
    )
    return correct, len(sentences)
