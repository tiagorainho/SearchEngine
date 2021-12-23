# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049


from collections import defaultdict
from typing import DefaultDict, Dict, List
from models.posting_list import PostingList, PostingListFactory, PostingType
from models.ranker import Ranker
import math


class BM25_Ranker(Ranker):
    k: float
    b: float
    documents_length: DefaultDict
    allowed_posting_types = [PostingType.FREQUENCY]
    posting_class: PostingList.__class__

    def __init__(self, posting_type: PostingType, *args, **kwargs):
        super().__init__(posting_type)
        self.documents_length = defaultdict(int)
        self.posting_class = PostingListFactory(posting_type)
        self.k = kwargs['k'] if 'k' in kwargs else None
        self.b = kwargs['b'] if 'b' in kwargs else None
    
    @staticmethod
    def load_tiny(line: str):
        return float(line)
    
    def merge_calculations(self, posting_list: PostingList):
        posting_list.idf = self.calculate_idf(posting_list)

    def order(self, term_to_posting_list: Dict[str, PostingList]) -> Dict[int, float]:
        query = list(term_to_posting_list.keys())

        tfs = dict()
        for token in query:
            tfs[token] = query.count(token)

        scores: DefaultDict[int, float] = defaultdict(float)  # doc_id, score

        dl_div_avgdl = self.metadata["doc_length_normalization"]

        for term, tf in tfs.items():
            posting_list = term_to_posting_list.get(term)
            if posting_list != None:
                docs: List[int] = posting_list.get_documents()

                for doc in docs:
                    freq = posting_list.posting_list[doc]
                    
                    idf = posting_list.tiny
                    tf = (freq * (self.k + 1)) / (freq + self.k * (1 - self.b + self.b * dl_div_avgdl[doc]))
                    
                    scores[doc] += idf * tf

        return sorted(scores.items(), key=lambda i: i[1], reverse=True)

    def document_repr(self, posting_list: PostingList):
        return ' '.join([f'{doc_id}-{freq}' for doc_id, freq in posting_list.posting_list.items()])

    def term_repr(self, posting_list: PostingList):
        return f'{self.document_repr(posting_list)}'

    def tiny_repr(self, posting_list: PostingList):
        return str(posting_list.idf)

    def metadata(self) -> Dict[str, object]:
        return {
            'ranker': 'BM25',
            'ranker_posting_class': 'frequency',
            'k': self.k,
            'b': self.b
        }

    def pos_processing(self) -> Dict[str, object]:
        avgdl = sum(self.documents_length.values()) / len(self.documents_length)
        documents_length_normalized = { doc: round(doc_length/avgdl, 3) for doc, doc_length in self.documents_length.items() }
        return {
            "doc_length_normalization": documents_length_normalized
        }
    
    def load_metadata(self, metadata: Dict[str, str]):
        # check if is the same ranker, posting list, etc
        if metadata['ranker'] != 'BM25':
            raise Exception(f'Ranker "{ metadata["ranker"] }" not compatible')
        if self.k == None: self.k = float(metadata['k'])
        if self.b == None: self.b = float(metadata['b'])
        self.metadata = metadata

    def load_posting_list(self, posting_list_class: PostingList.__class__, line: str) -> PostingList:

        posting_list = self.posting_class()

        for posting in line.split(' '):
            doc_id, freq = tuple(posting.split('-'))
            posting_list.posting_list[doc_id] = int(freq)

        return posting_list

    def after_add_tokens(self, term_to_postinglist: Dict[str, PostingList], tokens: List[str], doc_id: int):
        if doc_id not in self.documents_length:
            self.documents_length[doc_id] = len(tokens)

    def calculate_idf(self, posting_list: PostingList):
        return round(math.log10(len(self.documents_length)/len(posting_list.posting_list)), 3)
