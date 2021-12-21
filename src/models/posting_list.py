from __future__ import annotations
from typing import List
from enum import Enum

class PostingType(Enum):
    BOOLEAN = 'boolean'
    FREQUENCY = 'frequency'
    POSITIONAL = 'positional'

class PostingList:
    posting_type: PostingType

    def __init__(self, posting_type:PostingType)->None:
        self.posting_type = posting_type

    def add(self, doc_id:int, position:int)->None:
        pass

    def get_documents(self)->List[int]:
        pass

    @staticmethod
    def load(line:str)->PostingList:
        pass

    @staticmethod
    def merge(posting_lists:List[PostingList])->PostingList:
        pass

    def block_repr(self):
        pass

from models.posting_lists.boolean_posting_list import BooleanPostingList
from models.posting_lists.frequency_posting_list import FrequencyPostingList
from models.posting_lists.positional_posting_list import PositionalPostingList

posting_list_types = {
    PostingType.BOOLEAN: BooleanPostingList,
    PostingType.FREQUENCY: FrequencyPostingList,
    PostingType.POSITIONAL: PositionalPostingList
}

def PostingListFactory(posting_type:PostingType) -> PostingList:
    return posting_list_types[posting_type]

if __name__ == '__main__':
    pass