# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049


from __future__ import annotations
from enum import Enum
from typing import Dict, List, Tuple
from models.posting_list import PostingList, PostingType

class RankingMethod(Enum):
    TF_IDF = 'TF_IDF'
    TF_IDF_OPTIMIZED = 'TF_IDF_OPTIMIZED'
    BM25 = 'BM25'
    BM25_OPTIMIZED = 'BM25_OPTIMIZED'


class Ranker:
    allowed_posting_types: List[PostingType]

    def __init__(self, posting_type: PostingType, *args, **kwargs):
        pass

    def load_metadata(self, metadata: Dict[str, object]):
        self.metadata = metadata

    def metadata(self) -> Dict[str, object]:
        return dict()

    def pos_processing(self) -> Dict[str, object]:
        return dict()

    def before_add_tokens(self, term_to_postinglist: Dict[str, PostingList], tokens: List[str], doc_id: int):
        pass

    def after_add_tokens(self, term_to_postinglist: Dict[str, PostingList], tokens: List[str], doc_id: int):
        pass

    def document_repr(self, posting_list: PostingList):
        return str(posting_list)
    
    def merge_calculations(self, posting_list: PostingList):
        pass

    def term_repr(self, posting_list: PostingList):
        return str(posting_list)
    
    def tiny_repr(self, posting_list: PostingList):
        return None
    
    @staticmethod
    def load_tiny(line: str):
        return line

    def load_posting_list(self, posting_list_class: PostingList.__class__, line: str) -> PostingList:
        return posting_list_class.load(line)

    def order(self, term_to_posting_list: Dict[str, PostingList]) -> List[Tuple[int, float]]:
        res = list()
        for _, posting_list in term_to_posting_list.items():
            if posting_list == None:
                continue
            for doc_id in posting_list.get_documents():
                res.append((doc_id, 0))
        return res


from models.rankers.bm25 import BM25_Ranker
from models.rankers.tf_idf import TF_IDF_Ranker
from models.rankers.bm25_positional import BM25_Positional_Ranker
from models.rankers.td_idf_positional import TF_IDF_Positional_Ranker


ranking_methods:Dict[RankingMethod, Ranker] = {
    RankingMethod.TF_IDF: TF_IDF_Ranker,
    RankingMethod.BM25: BM25_Ranker,
    RankingMethod.BM25_OPTIMIZED: BM25_Positional_Ranker,
    RankingMethod.TF_IDF_OPTIMIZED: TF_IDF_Positional_Ranker,
}


def RankerFactory(method: RankingMethod) -> Ranker:
    return ranking_methods.get(method, Ranker)


if __name__ == '__main__':
    pass
