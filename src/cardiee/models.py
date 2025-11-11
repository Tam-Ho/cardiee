from typing import NamedTuple


class Flashcard(NamedTuple):
    id: int
    question: str
    answer: str
    deadline: str
