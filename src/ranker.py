
from __future__ import annotations
from enum import Enum
from collections import defaultdict
import math
from typing import Dict, DefaultDict, List

from models.posting_list import PostingList


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
    
    def calculate_tf(self, doc_id:int, tokens:List[str]) -> Dict[str, float]:
        pass

    def calculate_idf(self, posting_list:PostingList):
        pass

    def order(self, terms:List[str], posting_list:PostingList) -> List[int]:
        # query
        print(posting_list)

        # index
        for term in terms:
            pass

    
        return 1

class TF_IDF_Ranker(Ranker):
    documents_length: DefaultDict

    def __init__(self):
        self.documents_length = defaultdict(lambda: 0)

    
    def calculate_tf(self, doc_id:int, tokens:List[str]):
        """
        :param position: word position inside document
        :param doc_id: document ID
        """
        if doc_id not in self.documents_length:
            self.documents_length[doc_id] = len(tokens)

        term_frequencies = dict()

        for token in tokens:
            tf = len([t for t in tokens if t == token])
            term_frequencies[token] = self.uniform_tf(tf)
            
            
        return term_frequencies
    
    def uniform_tf(self, tf):
        return 1 + math.log10(tf)

    def calculate_idf(self, posting_list:PostingList):
        return round(math.log(len(self.documents_length.keys())/len(posting_list.posting_list.keys())),3)
    

    def calculate_weights(self, tfs):
        return [tf for tf in tfs.values()]

    def calculate_score(self):
        pass
    

    def uniform_weight(self, tfs):
        normalized_weights = {}
        weights = self.calculate_weights(tfs)
        sum_weights = sum([weight*weight for weight in weights])
        sqrt_weights = math.sqrt(sum_weights)

        for term, tf in tfs.items():
            normalized_weights[term] = tf / sqrt_weights

        return normalized_weights



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


