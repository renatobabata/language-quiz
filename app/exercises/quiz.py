from app.ai.base import AIProvider

INSTRUCTIONS = (
    "Read the text carefully, then answer each question by choosing one of "
    "the four options. You'll see immediately whether each answer is "
    "correct before moving to the next question."
)

QUIZ_PROMPT = """Based on the text below, create exactly 5 multiple-choice
questions (4 options each) to test reading comprehension. Write the
questions and options in the SAME language as the text. Respond with ONLY
valid JSON, no markdown, in this exact format:

[
  {{"question": "...", "options": ["...", "...", "...", "..."], "correct_index": 0}}
]

Text:
{text}
"""


def generate_quiz(text: str, provider: AIProvider) -> list[dict]:
    """Generates 5 multiple-choice comprehension questions for the given text."""
    return provider.generate_json(QUIZ_PROMPT.format(text=text))


def check_answer(questions: list[dict], question_index: int, answer_index: int) -> dict:
    """Checks a single answer against the stored quiz data.

    Used for the immediate per-question feedback flow: the student answers
    one question at a time and sees right away whether they got it right.
    """
    question = questions[question_index]
    correct_index = question["correct_index"]
    return {
        "correct": answer_index == correct_index,
        "correct_index": correct_index,
    }


def score_attempt(questions: list[dict], answers: list[int]) -> tuple[int, int]:
    """Scores a full attempt (all 5 answers) for the final results record."""
    correct = sum(
        1
        for question, given in zip(questions, answers, strict=False)
        if question["correct_index"] == given
    )
    return correct, len(questions)
