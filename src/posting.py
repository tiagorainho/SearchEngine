from typing import List


class Posting:
    docId: int
    start_position: List[int]
    occurrences: int

    def __init__(self, docId: int) -> None:
        self.docId = docId
        self.start_position = list()

    def add_start_position(self, position: int):
        self.start_position.append(position)
        self.occurrences += 1
