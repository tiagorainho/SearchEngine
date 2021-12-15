
from collections import defaultdict
from typing import Dict, List, Tuple
from models.posting import PostingType
from models.posting_list import PostingList, PostingListFactory
import math


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
            term = file.readline().split(self.delimiter, 1)[0]
            self.inverted_index[term] = None


    def search(self, terms: List[str]) -> List[int]:
        pass

    def light_search(self, terms: List[str]) -> List[int]:
        matches = []

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
                    line_term = line.split(self.delimiter)[0]

                    if term < line_term:
                        max = middle
                    elif term > line_term:
                        min = middle

                if term == line_term:
                    matches.extend(self.load(line)[1].get_documents())

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
        l = dict()
        for token in tokens:
            l[token] = 1 + math.log(sum([1 for t in tokens if t == token]))
        c = math.sqrt(sum(l.values()))

        for position, token in enumerate(tokens):
            posting_list:PostingList = self.inverted_index.get(token)

            if posting_list == None:
                posting_list = self.posting_list_class()
                self.inverted_index[token] = posting_list

            posting_list.add(doc_id, position)


            if 'term_weight' not in posting_list.__dict__:
                posting_list.term_weight = dict()

            posting_list.term_weight[doc_id] = l[token]*c

    def sorted_terms(self):
        """
        Returns a list of the terms sorted by alphabetic order

        :return: list of sorted terms based on the string comparison after normalizing to lower case letters
        """
        return sorted(list(self.inverted_index.keys()))

    def save(self, output_file: str) -> None:
        with open(output_file, 'w') as file:
            for term in self.sorted_terms():
                line = f'{ term }{ self.delimiter }{ self.inverted_index[term].block_repr() }\n'
                file.write(line)

    def load(self, line: str) -> Tuple[str, PostingList]:
        """"
        parts = line.split(self.delimiter, 1)
        posting_list_parts = parts[1].split('/')
        posting_list = self.posting_list_class.load(posting_list_parts[0])
        posting_list.term_weight = posting_list_parts[1]
        return parts[0], posting_list
        """
        parts = line.split(self.delimiter, 1)
        return parts[0], self.posting_list_class.load_blocks(parts[1])

    def __repr__(self):
        repr = ''
        for term, posting_list in self.inverted_index.items():
            repr += f'{term}: {posting_list if posting_list != None else "None"}\n'
        return repr
