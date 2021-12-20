from __future__ import annotations
from typing import Dict, List, Set
from models.posting import PostingType


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
    def load(line) -> BooleanPostingList:
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
            docid_freq = posting.split('-')
            new_posting_list[docid_freq[0]] = docid_freq[1]
        return new_posting_list
 
    def __repr__(self):
        return ' '.join([f'{doc_id}-{freq}' for doc_id, freq in self.posting_list.items()])


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



posting_list_types = {
    PostingType.BOOLEAN: BooleanPostingList,
    PostingType.FREQUENCY: FrequencyPostingList,
    PostingType.POSITIONAL: PositionalPostingList
}

def PostingListFactory(posting_type:PostingType) -> PostingList:
    return posting_list_types[posting_type]