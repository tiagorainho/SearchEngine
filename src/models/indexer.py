
from io import FileIO
from models.index import InvertedIndex
from typing import List
import os

class Indexer:
    inverted_index: InvertedIndex

    def __init__(self) -> None:
        self.inverted_index = InvertedIndex()


    def add(self, doc_id:int, tokens:List[str]) -> None:
        self.inverted_index.add(doc_id, tokens)

    
    def load_from_disk(self, path:str="../cache/") -> None:
        """
        
        """
        dirname = os.path.join(os.path.dirname(__file__), path)
        files = os.listdir(dirname)
        for file_name in files:
            if '.index' in file_name:
                with open(dirname + file_name, "rb") as file:
                    pass
                    #index = Spimi()
                    #index.inverted_index = pickle.load(file)
                    #self.add(index)
    
