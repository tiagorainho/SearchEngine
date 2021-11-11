
from typing import Dict, List
import pickle
from models.posting import Posting


class InvertedIndex:
    inverted_index: Dict[str, List[Posting]]
    file_indexes: List[str]

    # tratar de deixar posting lists em memoria com base nas pesquisas feitas


    def __init__(self, inverted_index:Dict[str, List[Posting]], files:List[str]) -> None:
        self.inverted_index = inverted_index
        self.file_indexes = files


    def search(self, terms:List[str]) -> List[int]:
        pass


    def add(self, term:str, posting_list:List[Posting]):
        pass


    def get(self, token) -> List[Posting]:
        pass
        

    def save(self, path="cache/") -> str:
        """
        :description: saves the inverted index to disk

        :param path: relative path to save the file
        :return: None
        """

        file = open(path + str(hash(self)) + ".index", "wb")
        pickle.dump(self.object_to_save(), file, pickle.HIGHEST_PROTOCOL)
        file.close()
        return file.name

    
    def object_to_save(self) -> object:
        pass

    def __repr__(self):
        repr = ''
        for term, posting_list in self.inverted_index.items():
            repr += f'{term}: {",".join([posting for posting in posting_list]) if posting_list != None else "None"}\n'
        return repr
    
    def __str__(self):
        return self.__repr__()

