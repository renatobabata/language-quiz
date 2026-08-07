"""Builds a crossword layout from a list of (word, clue) pairs.

This is a deterministic algorithm, not AI-generated: the AI (see crossword.py
in this same package) only extracts vocabulary and clues from the source
text; placing words on the grid is classic constraint-placement logic that
tries to intersect words on shared letters.
"""

from dataclasses import dataclass, field


@dataclass
class PlacedWord:
    word: str
    clue: str
    row: int
    col: int
    direction: str  # "across" or "down"
    number: int


@dataclass
class CrosswordResult:
    words: list[PlacedWord] = field(default_factory=list)
    height: int = 0
    width: int = 0


def _fits(grid: dict[tuple[int, int], str], word: str, row: int, col: int, direction: str) -> bool:
    for i, letter in enumerate(word):
        r = row + i if direction == "down" else row
        c = col + i if direction == "across" else col
        existing = grid.get((r, c))
        if existing is not None and existing != letter:
            return False
    return True


def _place(grid: dict[tuple[int, int], str], word: str, row: int, col: int, direction: str) -> None:
    for i, letter in enumerate(word):
        r = row + i if direction == "down" else row
        c = col + i if direction == "across" else col
        grid[(r, c)] = letter


def _find_intersection(grid: dict[tuple[int, int], str], word: str) -> tuple[int, int, str] | None:
    """Looks for a position where `word` crosses an already-placed letter."""
    for i, letter in enumerate(word):
        for (r, c), existing_letter in grid.items():
            if existing_letter != letter:
                continue
            row, col = r - i, c
            if _fits(grid, word, row, col, "down"):
                return row, col, "down"
            row, col = r, c - i
            if _fits(grid, word, row, col, "across"):
                return row, col, "across"
    return None


def generate_crossword(words_with_clues: list[tuple[str, str]]) -> CrosswordResult:
    """Builds the grid from a list of (word, clue) pairs.

    Words are normalized to uppercase with no spaces before entering the
    grid. The first word (usually the longest, since the list is sorted)
    anchors the grid; the rest try to intersect with what's already placed.
    A word with no found intersection is placed isolated on a new row.
    """
    normalized = [
        (w.strip().upper().replace(" ", ""), clue) for w, clue in words_with_clues if w.strip()
    ]
    normalized.sort(key=lambda pair: len(pair[0]), reverse=True)

    grid: dict[tuple[int, int], str] = {}
    placed: list[PlacedWord] = []
    next_free_row = 0

    for word, clue in normalized:
        if not placed:
            row, col, direction = 0, 0, "across"
        else:
            intersection = _find_intersection(grid, word)
            if intersection:
                row, col, direction = intersection
            else:
                row, col, direction = next_free_row, 0, "across"

        _place(grid, word, row, col, direction)
        placed.append(
            PlacedWord(
                word=word, clue=clue, row=row, col=col, direction=direction, number=len(placed) + 1
            )
        )
        next_free_row = max(next_free_row, row + (len(word) if direction == "down" else 1) + 1)

    if not grid:
        return CrosswordResult(words=[], height=0, width=0)

    min_row = min(r for r, _ in grid)
    min_col = min(c for _, c in grid)
    max_row = max(r for r, _ in grid)
    max_col = max(c for _, c in grid)

    for p in placed:
        p.row -= min_row
        p.col -= min_col

    return CrosswordResult(
        words=placed,
        height=max_row - min_row + 1,
        width=max_col - min_col + 1,
    )


def crossword_to_dict(result: CrosswordResult) -> dict:
    """Serializes the result for storage in the Exercise.data JSON column."""
    return {
        "height": result.height,
        "width": result.width,
        "words": [
            {
                "word": w.word,
                "clue": w.clue,
                "row": w.row,
                "col": w.col,
                "direction": w.direction,
                "number": w.number,
            }
            for w in result.words
        ],
    }
