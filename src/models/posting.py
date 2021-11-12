
from typing import List


class Posting:
    doc_id: int
    positions: List[int]
    occurrences: int

    def __init__(self, docId: int, positions:List[int] = []) -> None:
        self.doc_id = docId
        self.occurrences = 0
        self.positions = []
        if positions != []:
            self.add_multiple(positions)
        

    def add(self, position: int) -> None:
        self.positions.append(position)
        self.occurrences += 1
    
    def add_multiple(self, positions: List[int]) -> None:
        for position in positions:
            self.add(position)
    
    def __repr__(self) -> str:
        return '{' + str(self.doc_id) +':' + str(self.positions)[1:-1].replace(' ', '') + '}'