from typing import Dict, List
from src.models.abstract_index import AbstractIndex
from src.models.posting import Posting
import json

class Spimi(AbstractIndex):
    inverted_index: Dict[str, List[Posting]]
    

    def __init__(self) -> None:
        """
        :description: creates a new instance of a SPIMI indexer

        :return: None
        """
        self.inverted_index = dict()

    
    def add(self, doc_id:int, tokens:List[str], start_position:int=0) -> None:
        """
        :description: adds the tokens to the inverted index with the respective document id and start position of the first element of the tokens in the file

        :param doc_id: document id
        :param tokens: list of tokens contained in the document
        :param start_position = 0: start position of the first element of the token list
        :return: None
        """
        for position, token in enumerate(tokens):
            self._add(token, doc_id, position+start_position)


    def sorted_terms(self) -> List[str]:
        """
        :description: returns a list of the tokens sorted by alphabetic order

        :return: List[tokens]
        """
        return sorted(list(self.inverted_index.keys()), key=lambda term: term.lower())
    
    
    def _add(self, token:str, doc_id:int, position:int) -> None:
        """
        :description: private function that adds the document id and position to the Postings list of the respective token

        :param token: token to be added
        :param doc_id: document id
        :param position: position of the token in the respective document id
        :return: None
        """
        if token in self.inverted_index:
            self._update(token, doc_id, position)
        else:
            posting = Posting(doc_id)
            posting.add(position)
            self.inverted_index[token] = [posting]
            
    
    def _update(self, token:str, doc_id:int, position:int) -> None:
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
        
    
    def __hash__(self):
        inverted_index_json = json.dumps(self.sorted_terms())
        return hash(inverted_index_json)

    def object_to_save(self):
        return self.inverted_index

    def __repr__(self) -> str:
        str = ''
        for term, posting_list in self.inverted_index.items():
            postings_str = '['
            for i, posting in enumerate(posting_list):
                if i > 0: postings_str += ', '
                postings_str +=  repr(posting)
            postings_str += ']'
            str += "{term: \'" + term + "\', posting_list: " + postings_str + "}\n"
        return str