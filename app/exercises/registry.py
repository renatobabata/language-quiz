"""Maps each exercise type to its check/score functions and the key under
which its items are stored in Exercise.data.

This is what lets the /answer and /attempt endpoints in main.py stay generic
instead of being duplicated for every exercise type (quiz, cloze, and the
flashcard/crossword types coming next).
"""

from app.exercises import cloze, quiz

EXERCISE_TYPES: dict[str, dict] = {
    "quiz": {
        "data_key": "questions",
        "check_answer": quiz.check_answer,
        "score_attempt": quiz.score_attempt,
    },
    "cloze": {
        "data_key": "sentences",
        "check_answer": cloze.check_answer,
        "score_attempt": cloze.score_attempt,
    },
}
