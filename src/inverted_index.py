from typing import Dict, List
from hashlib import md5
from posting import Posting
from tokenizer import Tokenizer
from collections import defaultdict
import pickle
import json


class InvertedIndex:
    inverted_index: Dict[str, List[Posting]]
    hash: str

    def __init__(self) -> None:
        self.inverted_index = defaultdict(list)

    def add(self, tokenizer: Tokenizer):
        for (doc_id, tokens) in tokenizer.get_tokens().items():
            for token in tokens:
                self.add(token, doc_id)

        self.hash = json.dumps(self.inverted_index, sort_keys=True)
        self.hash = md5(self.hash.encode('utf-8'))
        self.hash = self.hash.hexdigest()

    def add(self, key: str, posting: Posting):
        self.inverted_index[key].append(posting)

    def has(self, key: str):
        return key in self.inverted_index

    def search(self, term: str):
        if term.lower() not in self.inverted_index:
            return None

        return self.inverted_index[term.lower()]

    def to_binary(self):
        return pickle.dump(self)
