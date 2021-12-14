
from __future__ import annotations
from enum import Enum
from typing import Any, Dict
from collections import defaultdict
import math


class RankingMethod(Enum):
    TF_IDF = 'tf_idf'
    BM25 = 'bm25'


class Ranker:

    def __init__(self, ranking_method:RankingMethod):
        pass


    @staticmethod
    def setup():
        pass

    def clear(self):
        pass

    def calculate_score(self):
        pass
    
    def add(self, doc_id:int, **kwargs):
        pass

    def relative_repr(self, doc_id:int):
        pass

    def global_repr(self):
        pass


class TF_IDF_Ranker(Ranker):
    
    def __init__(self):
        self.docs_length = defaultdict(lambda: 0)

    
    def add(self, doc_id:int, **kwargs):
        """
        :param position: word position inside document
        :param doc_id: document ID
        """
        self.docs_length[doc_id] += 1


    def relative_repr(self, doc_id:int):
        # N
        return f'{ str(TF_IDF_Ranker.variables["docs_length"][doc_id]) }'

    def global_repr(self):
        return f'{ str(len(TF_IDF_Ranker.variables["docs_length"])) }'
        
    def clear(self):
        pass

    def pre_calculatation(self, term:str):
        # idf
        return math.log10( len(TF_IDF_Ranker.variables["docs_length"])/sum() )


    def score(self, term:str):
        return self.pre_calculatation(term) + 1#etc



class BM25_Ranker(Ranker):
    pass


ranking_methods = {
    RankingMethod.TF_IDF: TF_IDF_Ranker,
    RankingMethod.BM25: BM25_Ranker
}


def RankerFactory(method:RankingMethod) -> Ranker:
    return ranking_methods[method]


if __name__ == '__main__':
    TF_IDF_Ranker.setup()
    print(TF_IDF_Ranker.variables)
    a = TF_IDF_Ranker()
    print(TF_IDF_Ranker.variables)
    b = TF_IDF_Ranker()
    print(TF_IDF_Ranker.variables)


