
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

    @staticmethod
    def order(term_to_posting_list:Dict[str, PostingList]) -> List[int]:
        return []

class TF_IDF_Ranker(Ranker):
    documents_length: DefaultDict

    def __init__(self):
        self.documents_length = defaultdict(lambda: 0)
    
    @staticmethod
    def order(term_to_posting_list:Dict[str, PostingList]) -> Dict[int, float]:
        # query
        query = term_to_posting_list.keys()

        tfs = dict()
        for token in query:
            tfs[token] = 1 + math.log10((sum([1 for t in query if t == token])))

        weights = tfs.values()
        sum_weights = sum([weight*weight for weight in weights])
        sqrt_weights = math.sqrt(sum_weights)

        scores:DefaultDict[int, float] = defaultdict(float) # doc_id, score
        for term, tf in tfs.items():
            posting_list = term_to_posting_list.get(term)
            if posting_list != None:
                docs:List[int] = posting_list.get_documents()
                for doc in docs:
                    ltc = (tf / sqrt_weights) * posting_list.idf
                    lnc = posting_list.term_weight[doc]
                    scores[doc] = ltc * lnc
        return sorted(scores.items(), key=lambda i: i[1])
    
    def calculate_tf(self, doc_id:int, tokens:List[str]):
        """
        :param position: word position inside document
        :param doc_id: document ID
        """
        if doc_id not in self.documents_length:
            self.documents_length[doc_id] = len(tokens)

        term_frequencies = dict()

        for token in tokens:
            tf = sum([1 for t in tokens if t == token])
            term_frequencies[token] = self.uniform_tf(tf)
            
        return term_frequencies
    
    def uniform_tf(self, tf):
        return 1 + math.log10(tf)

    def calculate_idf(self, posting_list:PostingList):
        return round(math.log(len(self.documents_length.keys())/len(posting_list.posting_list.keys())),3)
    

    def calculate_weights(self, tfs):
        return [tf for tf in tfs.values()]

    def calculate_score(self, l1,n1,c1, l2,t2,c2):
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
    pass


