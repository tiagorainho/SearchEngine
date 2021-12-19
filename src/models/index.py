
from types import FunctionType
from typing import Dict, List, Tuple
from models.posting import PostingType
from models.posting_list import PostingList, PostingListFactory
from ranker import Ranker


class InvertedIndex:
    inverted_index: Dict[str, PostingList]
    file: str
    posting_list_class: PostingList
    delimiter: str = ' '

    # tratar de deixar posting lists em memoria com base nas pesquisas feitas

    def __init__(self, inverted_index: Dict[str, PostingList], posting_type: PostingType, output_path: str = None) -> None:
        self.inverted_index = inverted_index if inverted_index != None else dict()
        self.posting_list_class = PostingListFactory(posting_type)
        self.file = output_path
        if inverted_index == None and output_path != None:
            self.load_dictionary(output_path)            

    def load_dictionary(self, file_name:str):
        with open(file_name, "r", encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            for line in lines:
                term_postinglist = line.split(self.delimiter, 1)
                term = term_postinglist[0]
                self.inverted_index[term] = None

    
    def search(self, terms: List[str], n:int, ranker:Ranker, show_score:bool=False) -> List[int] or List[Tuple[int, float]]:
        term_to_posting_lists = self.light_search(terms, ranker.load_posting_list)
        results = ranker.order(term_to_posting_lists)[:n]
        if not show_score:
            results = [tpl[0] for tpl in results]
        return results


    def light_search(self, terms: List[str], load_posting_list_func:FunctionType) -> Dict[str, PostingList]:
        matches = {term:None for term in terms}
        for term in terms:
            if term in self.inverted_index:
                posting_list:PostingList = self.inverted_index.get(term)
                # add posting list that is already found in memory
                if posting_list != None:
                    matches[term] = posting_list
                    terms.remove(term)
            else:
                # this term does not appear in the dictionary
                terms.remove(term)

        # early return if there is no more terms to search
        if len(terms) == 0: return matches

        # fetch the terms that are in the index file but not in memory and store them
        with open(self.file, "r", encoding='utf-8', errors='ignore') as file:
            
            file.seek(0, 2)
            file_size = file.tell()

            for term in terms:
                file.seek(0)
                min = 0
                max = file_size
                line = file.readline()
                line_term = line.split(self.delimiter)[0]

                while term != line_term and max - min > 1:
                    middle = int((max + min) / 2)
                    file.seek(middle)
                    file.readline()
                    line = file.readline()
                    line_term, line_posting_list = line.split(self.delimiter, 1)

                    if term < line_term:
                        max = middle
                    elif term > line_term:
                        min = middle

                if term == line_term:
                    posting_list = load_posting_list_func(line_posting_list)
                    matches[term] = posting_list
                    self.inverted_index[term] = posting_list

        return matches

    def clear(self):
        self.inverted_index.clear()

    def add_tokens(self, tokens: List[str], doc_id: int) -> None:
        """
        Adds the document id and position to the Postings list of the respective token

        :param token: token to be added
        :param doc_id: document id
        :param position: position of the token in the respective document id
        :return: None
        """
        for position, token in enumerate(tokens):
            posting_list:PostingList = self.inverted_index.get(token)

            if posting_list == None:
                posting_list = self.posting_list_class()
                self.inverted_index[token] = posting_list

            posting_list.add(doc_id, position)


    def sorted_terms(self):
        """
        Returns a list of the terms sorted by alphabetic order

        :return: list of sorted terms based on the string comparison after normalizing to lower case letters
        """
        return sorted(list(self.inverted_index.keys()))

    def save(self, output_file: str, ranker:Ranker=None) -> None:
        line_parser = lambda term: f'{ term }{ self.delimiter }{ self.inverted_index[term] }\n'
        if ranker != None:
            line_parser = lambda term: f'{ term }{ self.delimiter }{ ranker.document_repr(self.inverted_index[term]) }\n'

        with open(output_file, 'w') as file:
            for term in self.sorted_terms():
                line = line_parser(term)
                file.write(line)

    def load(self, line: str, ranker) -> Tuple[str, PostingList]:
        """"
        parts = line.split(self.delimiter, 1)
        posting_list_parts = parts[1].split('/')
        posting_list = self.posting_list_class.load(posting_list_parts[0])
        posting_list.term_weight = posting_list_parts[1]
        return parts[0], posting_list
        """
        term, posting_list_str = tuple(line.split(self.delimiter, 1))
        return term, ranker.load_posting_list(posting_list_str)

    def __repr__(self):
        repr = ''
        for term, posting_list in self.inverted_index.items():
            repr += f'{term}: {posting_list if posting_list != None else "None"}\n'
        return repr
