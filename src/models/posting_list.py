from typing import Dict
from models.posting import Posting


class PostingList():
    posting_list: Dict[int, Posting]

    def __init__(self):
        self.posting_list = dict()

    def add(self, posting:Posting):
        saved_posting = self.posting_list.get(posting.doc_id)
        if saved_posting == None:
            self.posting_list[posting.doc_id] = posting
        else:
            saved_posting.add_multiple(posting.positions)
    
    def __repr__(self):
        return ' '.join([str(posting) for posting in self.posting_list.values()])