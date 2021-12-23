# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049

from __future__ import annotations
from typing import List, Set
from models.posting_list import PostingList, PostingType


class BooleanPostingList(PostingList):
    posting_list: Set[int]

    def __init__(self):
        super().__init__(PostingType.BOOLEAN)
        self.posting_list = set()

    def add(self, doc_id:int, position:int=None):
        self.posting_list.add(doc_id)
    
    def get_documents(self) -> List[int]:
        return list(self.posting_list)

    @staticmethod
    def load(line:str) -> BooleanPostingList:
        new_posting_list = BooleanPostingList()
        for doc_id in line.split(' '):
            new_posting_list.posting_list.add(doc_id)
        return new_posting_list

    @staticmethod
    def merge(posting_lists:List[BooleanPostingList]) -> BooleanPostingList:
        new_posting_list:BooleanPostingList = max(posting_lists, key=lambda posting_list: len(posting_list.posting_list))
        posting_lists.remove(new_posting_list)
        for boolean_posting_list in posting_lists:
            new_posting_list.posting_list.update(boolean_posting_list.posting_list)
        return new_posting_list

    def __repr__(self):
        return ' '.join([str(posting) for posting in self.posting_list])
