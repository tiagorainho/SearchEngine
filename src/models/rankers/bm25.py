
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

    """
    added attributes to PostingList:
        - posting_list.term_weight : Dict[int, float]
    """

    def __init__(self, posting_type: PostingType, *args, **kwargs):
        super().__init__(posting_type)
        self.documents_length = defaultdict(int)
        self.posting_class = PostingListFactory(posting_type)
        self.k = kwargs['k']
        self.b = kwargs['b']

    def order(self, term_to_posting_list: Dict[str, PostingList]) -> Dict[int, float]:
        query = list(term_to_posting_list.keys())

        tfs = dict()
        for token in query:
            tfs[token] = BM25_Ranker.uniform_tf(query.count(token))

        scores: DefaultDict[int, float] = defaultdict(float)  # doc_id, score

        dl = self.metadata["document_length"]
        avgdl = self.metadata["average_document_length"]
        ratio_dl = dl/avgdl
        for term, tf in tfs.items():
            posting_list = term_to_posting_list.get(term)
            if posting_list != None:
                docs: List[int] = posting_list.get_documents()

                for doc in docs:
                    idf = posting_list.idf

                    # doc
                    freq = posting_list.term_weight[doc]
                    tf = (freq * (self.k + 1)) / (freq + self.k * (1 - self.b + self.b * ratio_dl ))
                    
                    scores[doc] += idf * tf

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
            "document_length": len(self.documents_length),
            "average_document_length": sum(self.documents_length.values()) / len(self.documents_length)
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
            if not hasattr(posting_list, 'term_weight'):
                BM25_Ranker.posting_list_init(posting_list)
            posting_list.term_weight[doc_id] = weights[token]


    def calculate_tf(self, doc_id: int, tokens: List[str]):
        """
        :param position: word position inside document
        :param doc_id: document ID
        """
        if doc_id not in self.documents_length:
            self.documents_length[doc_id] = len(tokens)

        term_frequencies = dict()
        for token in tokens:
            if token not in term_frequencies:
                term_frequencies[token] = BM25_Ranker.uniform_tf(tokens.count(token))

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
