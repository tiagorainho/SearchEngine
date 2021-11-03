
from models.spimi import Spimi
from models.abstract_index import AbstractIndex
from typing import Dict, List
import os
import pickle


class Indexer:
    indexes: Dict[str, AbstractIndex]
    max_block_size: int
    index_type: AbstractIndex.__class__

    def __init__(self, index_class: AbstractIndex.__class__, max_block_size: int) -> None:
        self.indexes = dict()
        self.max_block_size = max_block_size

    def add(self, doc_id: int, tokens: List[str]) -> None:
        # add tokens to old indexes

        # when index is full, create another index
        self.indexes[len(self.indexes)] = self.index_type()

    def load_from_disk(self, path: str = "../cache/") -> None:
        """

        """
        dirname = os.path.join(os.path.dirname(__file__), path)
        files = os.listdir(dirname)
        for file_name in files:
            if '.index' in file_name:
                with open(dirname + file_name, "rb") as file:
                    index = Spimi()
                    index.inverted_index = pickle.load(file)
                    self.add(index)
