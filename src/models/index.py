# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049


import os
from types import FunctionType
from typing import Dict, List, Tuple
from models.posting_list import PostingList, PostingListFactory, PostingType
from models.ranker import Ranker, RankerFactory, RankingMethod
import json
import io


class InvertedIndex:
    inverted_index: Dict[str, PostingList]
    file: str
    posting_list_class: PostingList
    delimiter: str = ' '
    metadata: Dict[str, object]
    index_start: int
    index_end: int
    tiny_dict: Dict[str, object]


    def __init__(self, inverted_index: Dict[str, PostingList], posting_type: PostingType=None, output_path: str = None) -> None:
        self.inverted_index = inverted_index if inverted_index != None else dict()
        self.file = output_path
        if inverted_index == None and output_path != None:
            self.load_dictionary(output_path)
            self.posting_list_class = PostingListFactory(PostingType(self.metadata['posting_class']))
            ranker:Ranker = Ranker(posting_type)
            if 'ranker' in self.metadata:
                ranker = RankerFactory(RankingMethod(self.metadata['ranker']))
            self.load_tiny_dictionary(f'{output_path}.tiny', ranker)
        if posting_type != None: self.posting_list_class = PostingListFactory(posting_type)

    
    def load_tiny_dictionary(self, file_name:str, ranker:Ranker):
        self.tiny_dict = dict()
        with open(file_name, "r", encoding='utf-8', errors='ignore') as file:
            for line in file:
                term, obj = tuple(line.split(' ', maxsplit=1))
                self.tiny_dict[term] = ranker.load_tiny(obj)

    def load_dictionary(self, file_name:str):
        self.metadata = dict()

        with open(file_name, "r", encoding='utf-8', errors='ignore') as file:
            num_lines = 0
            for line in file:
                num_lines += 1

            # get pre-processing metadata
            file.seek(0)
            line = file.readline()
            self.metadata = json.load(io.StringIO(line))
            self.index_start = file.tell()

            # read posting lists
            file.seek(self.index_start)
            i=0
            while file:
                line = file.readline()
                term_postinglist = line.split(self.delimiter, 1)
                term = term_postinglist[0]
                self.inverted_index[term] = None
                if i+3 >= num_lines:
                    self.index_end = file.tell()
                    break
                i += 1

            # get pos-processing metadata
            file.seek(self.index_end)
            posprocessing_metadata = file.readline()
            metadata_pos_processing = json.load(io.StringIO(posprocessing_metadata))
            for key, value in metadata_pos_processing.items():
                self.metadata[key] = value
    
    def search(self, terms: List[str], n:int, ranker:Ranker, show_score:bool=False) -> List[int] or List[Tuple[int, float]]:
        if ranker == None:
            ranker = Ranker(self.posting_list_class().posting_type)
        ranker.load_metadata(self.metadata)
        term_to_posting_lists = self.light_search(terms, ranker.load_posting_list)
        results = ranker.order(terms, term_to_posting_lists)
        if len(results) > n: results = results[:n]
        
        if not show_score:
            results = [tpl[0] for tpl in results]
        return results

    def fetch_terms(self, terms: List[object], file_name:str, start:int=0, end:int=None) -> Dict[object, str]:

        matches:Dict[str, str] = dict()

        # fetch the terms from disk
        with open(file_name, "r", encoding='utf-8', errors='ignore') as file:
            if end == None:
                file.seek(0, os.SEEK_END)
                end = file.tell()
                file.seek(start)
            
            for term in terms:
                min = start
                max = end
                file.seek(min)
                line = file.readline()
                term_type = type(term)
                line_term, line_posting_list = line.split(self.delimiter, 1)

                while term != line_term and max - min > 1:
                    middle = int((max + min) / 2)
                    file.seek(middle)
                    file.readline()
                    line = file.readline()

                    try:
                        line_term, line_posting_list = line.split(self.delimiter, 1)
                        line_term = term_type(line_term)
                    except Exception:
                        continue

                    if term < line_term:
                        max = middle
                    elif term > line_term:
                        min = middle

                if term == line_term:
                    matches[term] = line_posting_list.replace('\n', '')
        return matches

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
        fetched_terms = self.fetch_terms(terms, self.file, self.index_start, self.index_end)
        for term, line in fetched_terms.items():
            posting_list = load_posting_list_func(line)
            matches[term] = posting_list
            self.inverted_index[term] = posting_list
            self.inverted_index[term].tiny = self.tiny_dict.get(term, None)
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
        return term, ranker.load_posting_list(posting_list_str)

    def __repr__(self):
        repr = ''
        for term, posting_list in self.inverted_index.items():
            repr += f'{term}: {posting_list if posting_list != None else "None"}\n'
        return repr
