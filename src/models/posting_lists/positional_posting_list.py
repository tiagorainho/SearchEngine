from __future__ import annotations
from typing import Dict, List
from models.posting_list import PostingList, PostingType


class PositionalPostingList(PostingList):

    posting_list: Dict[int, List[int]]

    def __init__(self):
        super().__init__(PostingType.POSITIONAL)
        self.posting_list = dict()

    def add(self, doc_id:int, position:int):
        saved_posting = self.posting_list.get(doc_id)
        if saved_posting == None:
            self.posting_list[doc_id] = [position]
        else:
            saved_posting.append(position)

    def get_documents(self) -> List[int]:
        return list(self.posting_list.keys())

    @staticmethod
    def load(line:str) -> PositionalPostingList:
        new_posting_list = PositionalPostingList()
        for posting_list_line in line.split(' '):
            parts = posting_list_line.split(':')
            doc_id = parts[0]
            for positions in parts[1:]:
                for position in positions.split(','):
                    new_posting_list.add(doc_id, int(position))
        return new_posting_list

    @staticmethod
    def merge(posting_lists:List[PositionalPostingList]) -> PositionalPostingList:
        new_posting_list:PositionalPostingList = max(posting_lists, key=lambda posting_list: len(posting_list.posting_list))
        posting_lists.remove(new_posting_list)
        for posting_list in posting_lists:
            for doc_id, positions in posting_list.posting_list.items():
                for position in positions:
                    new_posting_list.add(doc_id, position)
        return new_posting_list

    def __repr__(self):
        return ' '.join([f"{str(doc_id)}:{','.join([str(position) for position in postings_list])}" for doc_id, postings_list in self.posting_list.items()])
