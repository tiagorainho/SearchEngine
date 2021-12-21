
from __future__ import annotations
from enum import Enum
from collections import defaultdict
from typing import Dict, DefaultDict, List, Tuple
from models.posting import PostingType
from models.posting_list import PostingList, PostingListFactory
import math


class RankingMethod(Enum):
    TF_IDF = 'tf_idf'
    BM25 = 'bm25'


class Ranker:
    allowed_posting_types: List[PostingType]

    def __init__(self, posting_type: PostingType):
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

    def term_repr(self, posting_list: PostingList):
        return str(posting_list)

    def load_posting_list(self, posting_list_class: PostingList.__class__, line: str) -> PostingList:
        return posting_list_class.load(line)

    def order(self, term_to_posting_list: Dict[str, PostingList]) -> List[Tuple[int, float]]:
        res = list()
        for term, posting_list in term_to_posting_list.items():
            if posting_list == None:
                continue
            for doc_id in posting_list.get_documents():
                res.append((doc_id, 0))
        return res

class TF_IDF_Ranker(Ranker):
    documents_length: DefaultDict
    allowed_posting_types = [PostingType.FREQUENCY]
    posting_class: PostingList.__class__

    """
    added attributes to PostingList:
        - posting_list.tf_weight : Dict[int, float]
    """

    def __init__(self, posting_type: PostingType):
        super().__init__(posting_type)
        if posting_type not in self.allowed_posting_types:
            raise Exception(
                f'{ posting_type } not supported for {self.__class__}')
        self.documents_length = defaultdict(int)
        self.posting_class = PostingListFactory(posting_type)

    def load_metadata(self, metadata: Dict[str, str]):
        # check if is the same ranker, posting list, etc
        if metadata['ranker'] != 'TF_IDF':
            raise Exception(f'Ranker "{ metadata["ranker"] }" not compatible')
        self.metadata = metadata

    def metadata(self) -> Dict[str, object]:
        return {
            'ranker': 'TF_IDF',
            'posting_class': 'frequency'
        }

    def pos_processing(self) -> Dict[str, object]:
        return {
            'some_key': 'some_value'
        }

    def order(self, term_to_posting_list: Dict[str, PostingList]) -> List[Tuple[int, float]]:

        query = term_to_posting_list.keys()

        tfs = dict()
        for token in query:
            tfs[token] = TF_IDF_Ranker.uniform_tf(
                sum([1 for t in query if t == token]))

        weights = tfs.values()
        sum_weights = sum([weight*weight for weight in weights])
        sqrt_weights = math.sqrt(sum_weights)

        scores: DefaultDict[int, float] = defaultdict(float)  # doc_id, score
        for term, tf in tfs.items():
            posting_list = term_to_posting_list.get(term)
            if posting_list != None:
                docs: List[int] = posting_list.get_documents()
                for doc in docs:
                    # query
                    ltc = (tf / sqrt_weights) * posting_list.idf
                    # documents
                    lnc = posting_list.tf_weight[doc]

                    scores[doc] = ltc * lnc

        return sorted(scores.items(), key=lambda i: i[1], reverse=True)

    def document_repr(self, posting_list: PostingList):
        return ' '.join([f'{doc_id}-{freq}/{round(posting_list.tf_weight[doc_id], 3)}' for doc_id, freq in posting_list.posting_list.items()])

    def term_repr(self, posting_list: PostingList):
        idf = self.calculate_idf(posting_list)
        return f'{self.document_repr(posting_list)}#{idf}'

    @staticmethod
    def posting_list_init(posting_list: PostingList):
        posting_list.tf_weight = defaultdict(int)

    def load_posting_list(self, posting_list_class: PostingList.__class__, line: str) -> PostingList:

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
            posting_list.tf_weight[doc_id] = float(weight)

        return posting_list

    def after_add_tokens(self, term_to_postinglist: Dict[str, PostingList], tokens: List[str], doc_id: int):
        tfs = self.calculate_tf(doc_id, tokens)
        weights = TF_IDF_Ranker.uniform_weight(tfs)
        for token in tokens:
            posting_list: PostingList = term_to_postinglist[token]
            if 'tf_weight' not in posting_list.__dict__:
                TF_IDF_Ranker.posting_list_init(posting_list)
            posting_list.tf_weight[doc_id] = weights[token]

    def calculate_tf(self, doc_id: int, tokens: List[str]):
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

    def calculate_idf(self, posting_list: PostingList):
        return round(math.log(len(self.documents_length.keys())/len(posting_list.posting_list.keys())), 3)

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
    k: float
    b: float
    documents_length: DefaultDict
    allowed_posting_types = [PostingType.FREQUENCY]
    posting_class: PostingList.__class__

    """
    added attributes to PostingList:
        - posting_list.term_weight : Dict[int, float]
    """

    def __init__(self, posting_type: PostingType, k, b):
        super().__init__(posting_type)
        self.documents_length = defaultdict(int)
        self.posting_class = PostingListFactory(posting_type)
        self.k = k
        self.b = b

    def order(self, term_to_posting_list: Dict[str, PostingList]) -> Dict[int, float]:
        query = term_to_posting_list.keys()

        tfs = dict()
        for token in query:
            tfs[token] = BM25_Ranker.uniform_tf(
                sum([1 for t in query if t == token]))

        weights = tfs.values()
        sum_weights = sum([weight*weight for weight in weights])
        sqrt_weights = math.sqrt(sum_weights)
        scores: DefaultDict[int, float] = defaultdict(float)  # doc_id, score

        for term, tf in tfs.items():
            posting_list = term_to_posting_list.get(term)
            if posting_list != None:
                docs: List[int] = posting_list.get_documents()
                normalized_weight = (tf / sqrt_weights)

                for doc in docs:
                    dl = self.metadata["document_length"]
                    avgdl = self.metadata["average_document_length"]
                    scores[doc] = posting_list.idf
                    scores[doc] *= normalized_weight * (self.k + 1)
                    scores[doc] /= self.k * ((1-self.b) + self.b * dl /
                                        avgdl) + normalized_weight
                    scores[doc] *= posting_list.idf * \
                        posting_list.term_weight[doc]

        return sorted(scores.items(), key=lambda i: i[1], reverse=True)

    def document_repr(self, posting_list: PostingList):
        return ' '.join([f'{doc_id}-{freq}/{round(posting_list.term_weight[doc_id], 3)}' for doc_id, freq in posting_list.posting_list.items()])

    def term_repr(self, posting_list: PostingList):
        idf = self.calculate_idf(posting_list)
        return f'{self.document_repr(posting_list)}#{idf}'

    def metadata(self) -> Dict[str, object]:
        return {
            'ranker': 'BM25',
            'posting_class': 'frequency'
        }

    def pos_processing(self) -> Dict[str, object]:
        return {
            "document_length": len(self.documents_length.keys()),
            "average_document_length": sum(self.documents_length.values()) / len(self.documents_length.keys())
        }
    
    def load_metadata(self, metadata: Dict[str, str]):
        # check if is the same ranker, posting list, etc
        if metadata['ranker'] != 'BM25':
            raise Exception(f'Ranker "{ metadata["ranker"] }" not compatible')
        self.metadata = metadata

    @ staticmethod
    def posting_list_init(posting_list: PostingList):
        posting_list.term_weight = defaultdict(int)

    def load_posting_list(self, posting_list_class: PostingList.__class__, line: str) -> PostingList:

        posting_list = self.posting_class()
        BM25_Ranker.posting_list_init(posting_list)

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

    def after_add_tokens(self, term_to_postinglist: Dict[str, PostingList], tokens: List[str], doc_id: int):
        tfs = self.calculate_tf(doc_id, tokens)
        weights = BM25_Ranker.uniform_weight(tfs)

        for token in tokens:
            posting_list: PostingList = term_to_postinglist[token]

            if 'term_weight' not in posting_list.__dict__:
                BM25_Ranker.posting_list_init(posting_list)

            dl = sum(self.documents_length.values())
            avgdl = dl / len(self.documents_length.keys())
            posting_list.term_weight[doc_id] = weights[token] * (self.k + 1)
            posting_list.term_weight[doc_id] /= self.k * \
                ((1-self.b) + self.b * dl / avgdl) + weights[token]


    def calculate_tf(self, doc_id: int, tokens: List[str]):
        """
        :param position: word position inside document
        :param doc_id: document ID
        """
        if doc_id not in self.documents_length:
            self.documents_length[doc_id] = len(tokens)

        term_frequencies = dict()

        for token in tokens:
            tf = sum([1 for t in tokens if t == token])
            term_frequencies[token] = BM25_Ranker.uniform_tf(tf)

        return term_frequencies

    @ staticmethod
    def uniform_tf(tf):
        return 1 + math.log10(tf)

    def calculate_idf(self, posting_list: PostingList):
        return round(math.log(len(self.documents_length.keys())/len(posting_list.posting_list.keys())), 3)

    @ staticmethod
    def calculate_weights(tfs):
        return [tf for tf in tfs.values()]

    @ staticmethod
    def uniform_weight(tfs):
        normalized_weights = {}
        weights = BM25_Ranker.calculate_weights(tfs)
        sum_weights = sum([weight*weight for weight in weights])
        sqrt_weights = math.sqrt(sum_weights)

        for term, tf in tfs.items():
            normalized_weights[term] = tf / sqrt_weights

        return normalized_weights


ranking_methods = {
    RankingMethod.TF_IDF: TF_IDF_Ranker,
    RankingMethod.BM25: BM25_Ranker


}


def RankerFactory(method: RankingMethod) -> Ranker:
    return ranking_methods[method]


if __name__ == '__main__':
    pass
