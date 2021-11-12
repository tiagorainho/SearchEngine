
from typing import Dict, List
import pickle, os
from models.posting import Posting


class InvertedIndex:
    inverted_index: Dict[str, List[Posting]]

    # tratar de deixar posting lists em memoria com base nas pesquisas feitas


    def __init__(self, inverted_index:Dict[str, List[Posting]]) -> None:
        self.inverted_index = inverted_index if inverted_index != None else dict()
    

    def add_token(self, token:str, doc_id:int, position:int) -> None:
        """
        Adds the document id and position to the Postings list of the respective token

        :param token: token to be added
        :param doc_id: document id
        :param position: position of the token in the respective document id
        :return: None
        """
        if token in self.inverted_index:
            self._update_posting_list(token, doc_id, position)
        else:
            posting = Posting(doc_id)
            posting.add(position)
            self.inverted_index[token] = [posting]
    

    def _update_posting_list(self, token:str, doc_id:int, position:int) -> None:
        """
        :description: private function that updates or created a Posting inside the respective token Posting list

        :param token: token to be added
        :param doc_id: document id
        :param position: position of the token in the respective document id
        :return: None
        """
        for posting in self.inverted_index[token]:
            if posting.doc_id == doc_id:
                posting.add(position)
                return
        posting = Posting(doc_id)
        posting.add(position)
        self.inverted_index[token].append(posting)

    
    def sorted_terms(self):
        """
        Returns a list of the terms sorted by alphabetic order

        :return: list of sorted terms based on the string comparison after normalizing to lower case letters
        """
        return sorted(list(self.inverted_index.keys()), key=lambda term: term.lower())


    def search(self, terms:List[str]) -> List[int]:
        pass


    def save(self, output_file:str) -> None:
        with open(output_file, 'w') as file:
            for term in self.sorted_terms():
                lines = f"{term} {' '.join([str(posting) for posting in self.inverted_index[term]])}\n"
                file.write(lines)


    def object_to_save(self) -> object:
        pass


    def __repr__(self):
        repr = ''
        for term, posting_list in self.inverted_index.items():
            repr += f'{term}: {",".join([posting for posting in posting_list]) if posting_list != None else "None"}\n'
        return repr

    
    def __str__(self):
        return self.__repr__()

