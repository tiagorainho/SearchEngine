
from typing import List
import pickle


class AbstractIndex:

    def __init__(self) -> None:
        pass

    def add(self, doc_id:int, tokens:List[str], start_position:int=0):
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