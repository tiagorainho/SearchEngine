
from __future__ import annotations
from enum import Enum
from collections import defaultdict
from typing import Dict, DefaultDict, List
from models.posting import PostingType
from models.posting_list import PostingList, PostingListFactory
import math

class RankingMethod(Enum):
    TF_IDF = 'tf_idf'
    BM25 = 'bm25'


class Ranker:
    allowed_posting_types:List[PostingType]


    def __init__(self, posting_type:PostingType):
        if posting_type not in self.allowed_posting_types:
            raise Exception(f'{ posting_type } not supported for {self.__class__}')

    def before_add_tokens(self, term_to_postinglist: Dict[str, PostingList], tokens:List[str], doc_id:int):
        pass

    def after_add_tokens(self, term_to_postinglist: Dict[str, PostingList], tokens:List[str], doc_id:int):
        pass

    def document_repr(self, posting_list:PostingList):
        pass

    def term_repr(self, posting_list:PostingList):
        pass

    def load_posting_list(posting_list_class:PostingList.__class__, line:str) -> PostingList:
        pass

    def order(term_to_posting_list:Dict[str, PostingList]) -> Dict[int, float]:
        pass



class TF_IDF_Ranker(Ranker):
    documents_length: DefaultDict
    allowed_posting_types = [PostingType.FREQUENCY]
    posting_class: PostingList.__class__

    """
    added attributes to PostingList:
        - posting_list.term_weight : Dict[int, float]
    """

    def __init__(self, posting_type:PostingType):
        super().__init__(posting_type)
        self.documents_length = defaultdict(int)
        self.posting_class = PostingListFactory(posting_type)
    
    def order(self, term_to_posting_list:Dict[str, PostingList]) -> Dict[int, float]:
        query = term_to_posting_list.keys()

        tfs = dict()
        for token in query:
            tfs[token] = TF_IDF_Ranker.uniform_tf(sum([1 for t in query if t == token]))

        weights = tfs.values()
        sum_weights = sum([weight*weight for weight in weights])
        sqrt_weights = math.sqrt(sum_weights)

        scores:DefaultDict[int, float] = defaultdict(float) # doc_id, score
        for term, tf in tfs.items():
            posting_list = term_to_posting_list.get(term)
            if posting_list != None:
                docs:List[int] = posting_list.get_documents()
                for doc in docs:
                    # query
                    ltc = (tf / sqrt_weights) * posting_list.idf
                    # documents
                    lnc = posting_list.term_weight[doc]

                    scores[doc] = ltc * lnc

        return sorted(scores.items(), key=lambda i: i[1], reverse=True)
    
    def document_repr(self, posting_list:PostingList):
        return ' '.join([f'{doc_id}-{freq}/{round(posting_list.term_weight[doc_id], 3)}' for doc_id, freq in posting_list.posting_list.items()])

    def term_repr(self, posting_list:PostingList):
        idf = self.calculate_idf(posting_list)
        return f'{self.document_repr(posting_list)}#{idf}'
    
    @staticmethod
    def posting_list_init(posting_list:PostingList):
        posting_list.term_weight = defaultdict(int)
    
    def load_posting_list(self, line:str) -> PostingList:

        posting_list = self.posting_class()
        TF_IDF_Ranker.posting_list_init(posting_list)

        parts = line.split('#')
        posting_list_str = parts[0]
        if len(parts) > 1:
            idf = parts[1]
            posting_list.idf = float(idf)

        for posting in posting_list_str.split(' '):
            posting_str, weight = tuple(posting.split('/'))
            doc_id, freq = tuple(posting_str.split('-'))
            posting_list.posting_list[doc_id] = int(freq)
            posting_list.term_weight[doc_id] = float(weight)

        return posting_list

    def after_add_tokens(self, term_to_postinglist: Dict[str, PostingList], tokens:List[str], doc_id:int):
        tfs = self.calculate_tf(doc_id, tokens)
        weights =  TF_IDF_Ranker.uniform_weight(tfs)
        for token in tokens:
            posting_list:PostingList = term_to_postinglist[token]
            if 'term_weight' not in posting_list.__dict__:
                TF_IDF_Ranker.posting_list_init(posting_list)
            posting_list.term_weight[doc_id] = weights[token]
    
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
            term_frequencies[token] = TF_IDF_Ranker.uniform_tf(tf)
            
        return term_frequencies
    
    @staticmethod
    def uniform_tf(tf):
        return 1 + math.log10(tf)

    def calculate_idf(self, posting_list:PostingList):
        return round(math.log(len(self.documents_length.keys())/len(posting_list.posting_list.keys())),3)
    
    @staticmethod
    def calculate_weights(tfs):
        return [tf for tf in tfs.values()]

    @staticmethod
    def uniform_weight(tfs):
        normalized_weights = {}
        weights = TF_IDF_Ranker.calculate_weights(tfs)
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


