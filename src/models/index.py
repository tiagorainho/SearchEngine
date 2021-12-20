
from types import FunctionType
from typing import Dict, List, Tuple
from models.posting import PostingType
from models.posting_list import PostingList, PostingListFactory
from ranker import Ranker
import json
import os
import io


class InvertedIndex:
    inverted_index: Dict[str, PostingList]
    file: str
    posting_list_class: PostingList
    delimiter: str = ' '
    metadata: Dict[str, object]
    metadata_start: int
    metadata_end: int

    # tratar de deixar posting lists em memoria com base nas pesquisas feitas

    def __init__(self, inverted_index: Dict[str, PostingList], posting_type: PostingType, output_path: str = None) -> None:
        self.inverted_index = inverted_index if inverted_index != None else dict()
        self.posting_list_class = PostingListFactory(posting_type)
        self.file = output_path
        if inverted_index == None and output_path != None:
            self.load_dictionary(output_path)

    def load_dictionary(self, file_name:str):
        self.metadata = dict()

        with open(file_name, "r", encoding='utf-8', errors='ignore') as file:
            # get pre-processing metadata
            line = file.readline()
            self.metadata = json.load(io.StringIO(line))
            self.metadata_start = file.tell()

            # get pos-processing metadata
            file.seek(0, os.SEEK_END)
            self.metadata_end = file.tell()
            try:
                file.seek(file.tell() - 2, os.SEEK_SET)
                while file.read(1) != '\n':
                    self.metadata_end -= 2
                    file.seek(file.tell() - 2, os.SEEK_SET)
            except Exception:
                raise Exception("Error fetching pos-processing metadata")
            
            posprocessing_metadata = file.readline()
            metadata_pos_processing = json.load(io.StringIO(posprocessing_metadata))

            for key, value in metadata_pos_processing.items():
                self.metadata[key] = value

            file.seek(self.metadata_start)
            curr_pos = self.metadata_start
            while curr_pos >= self.metadata_start and curr_pos < self.metadata_end:
                line = file.readline()
                term_postinglist = line.split(self.delimiter, 1)
                term = term_postinglist[0]
                self.inverted_index[term] = None
                curr_pos = file.tell()
    
    def search(self, terms: List[str], n:int, ranker:Ranker, show_score:bool=False) -> List[int] or List[Tuple[int, float]]:
        if ranker == None:
            ranker = Ranker(self.posting_list_class().posting_type)

        ranker.load_metadata(self.metadata)
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
            
            for term in terms:
                min = self.metadata_start
                max = self.metadata_end
                file.seek(min)
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
                    posting_list = load_posting_list_func(self.posting_list_class, line_posting_list)
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
    
    def save_data(self, ouput_path:str, data:Dict[str, object]):
        with open(ouput_path, 'a+') as output_file:
            output_file.write(f'{json.dumps(data)}\n')

    def save(self, output_file: str, ranker:Ranker) -> None:
        with open(output_file, 'w') as file:
            for term in self.sorted_terms():
                line = f'{ term }{ self.delimiter }{ ranker.document_repr(self.inverted_index[term]) }\n'
                file.write(line)
    
    def load(self, line: str, ranker:Ranker) -> Tuple[str, PostingList]:
        term, posting_list_str = tuple(line.split(self.delimiter, 1))
        return term, ranker.load_posting_list(self.posting_list_class, posting_list_str)

    def __repr__(self):
        repr = ''
        for term, posting_list in self.inverted_index.items():
            repr += f'{term}: {posting_list if posting_list != None else "None"}\n'
        return repr
