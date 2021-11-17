
from io import FileIO
import io
from typing import Dict, List, Set, Tuple
from models.posting import PostingType
from models.posting_list import PostingList, PostingListFactory
from pathlib import Path
from time import sleep


class InvertedIndex:
    inverted_index: Dict[str, PostingList]
    file: FileIO
    posting_list_class: PostingList
    delimiter: str = ' '

    # tratar de deixar posting lists em memoria com base nas pesquisas feitas

    def __init__(self, inverted_index: Dict[str, PostingList], posting_type: PostingType, output_path: str = None) -> None:
        self.inverted_index = inverted_index if inverted_index != None else dict()
        self.posting_list_class = PostingListFactory(posting_type)
        self.file = open(output_path, "r") if output_path != None else None

    def light_search(self, terms: List[str]) -> List[int]:
        matches = []
        self.file.seek(0, 2)
        file_size = self.file.tell()

        for term in terms:
            min = 0
            max = file_size
            middle = (max + min) / 2
            self.file.seek(0)
            line = self.file.readline()
            line_term = line.split(self.delimiter)[0]

            while term != line_term or max - min == 0:
                middle = int((max + min) / 2)
                self.file.seek(middle)
                self.file.readline()
                line = self.file.readline()
                line_term = line.split(self.delimiter)[0]

                if term < line_term:
                    max = middle
                elif term > line_term:
                    min = middle

            matches.append(line)

        return matches

    def clear(self):
        self.inverted_index.clear()

    def add_token(self, token: str, doc_id: int, position: int) -> None:
        """
        Adds the document id and position to the Postings list of the respective token

        :param token: token to be added
        :param doc_id: document id
        :param position: position of the token in the respective document id
        :return: None
        """
        posting_list = self.inverted_index.get(token)

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

    def save(self, output_file: str) -> None:
        with open(output_file, 'w') as file:
            for term in self.sorted_terms():
                line = f'{ term }{ self.delimiter }{ self.inverted_index[term] }\n'
                file.write(line)

    def load(self, line: str) -> Tuple[str, PostingList]:
        parts = line.split(self.delimiter, 1)
        return parts[0], self.posting_list_class.load(parts[1])

    def __repr__(self):
        repr = ''
        for term, posting_list in self.inverted_index.items():
            repr += f'{term}: {posting_list if posting_list != None else "None"}\n'
        return repr
