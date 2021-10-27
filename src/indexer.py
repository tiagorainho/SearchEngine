from typing import Dict, Set
from inverted_index import InvertedIndex
import pickle


class Indexer:
    indexes: Dict[str, InvertedIndex]

    def __init__(self) -> None:
        self.indexes = dict()

    def add(self, index: InvertedIndex):
        self.indexes[index.hash] = index

    def load_from_disk(self, path: str):
        with open(path) as file:
            self.indexes(pickle.load(file))

    def save_to_disk(self, keys: Set[str]):
        for key in keys.intersection(self.indexes.keys()):
            index = self.indexes[key]
            with open(f"cache/{index.hash}") as file:
                pickle.dumps(self.indexes[key], file)
