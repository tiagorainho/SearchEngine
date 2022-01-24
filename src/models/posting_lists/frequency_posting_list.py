# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049

from __future__ import annotations
from typing import Dict, List
from models.posting_list import PostingList, PostingType


class FrequencyPostingList(PostingList):
    posting_list: Dict[int, int]

    def __init__(self):
        super().__init__(PostingType.FREQUENCY)
        self.posting_list = dict()

    def add(self, doc_id:int, position:int=None):
        freq = self.posting_list.get(doc_id)
        if freq == None: self.posting_list[doc_id] = 1
        else: self.posting_list[doc_id] = freq + 1
        

    def get_documents(self) -> List[int]:
        return list(self.posting_list.keys())
        

    @staticmethod
    def merge(posting_lists:List[FrequencyPostingList]) -> FrequencyPostingList:
        new_posting_list:FrequencyPostingList = max(posting_lists, key=lambda posting_list: len(posting_list.posting_list))
        posting_lists.remove(new_posting_list)
        for posting_list in posting_lists:
            for doc_id, freq in posting_list.posting_list.items():
                new_freq = new_posting_list.posting_list.get(doc_id)
                if new_freq == None:
                    new_posting_list.posting_list[doc_id] = freq
                else:
                    new_posting_list.posting_list[doc_id] = freq + new_freq
        return new_posting_list

    @staticmethod
    def load(line:str)->PostingList:
        new_posting_list = FrequencyPostingList()
        for posting in line.split(' '):
            docid_freq = posting.split(':')
            new_posting_list.posting_list[docid_freq[0]] = docid_freq[1]
        return new_posting_list
 
    def __repr__(self):
        return ' '.join([f'{doc_id}:{freq}' for doc_id, freq in self.posting_list.items()])
    
    def repr(self):
        return self.__repr__()
