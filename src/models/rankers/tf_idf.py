# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049


from collections import defaultdict
from typing import DefaultDict, Dict, List, Tuple
from models.posting_list import PostingList, PostingListFactory, PostingType
from models.ranker import Ranker
import math

class TF_IDF_Ranker(Ranker):
    documents_length: DefaultDict
    allowed_posting_types = [PostingType.FREQUENCY]
    posting_class: PostingList.__class__

    """
    added attributes to PostingList:
        - posting_list.tf_weight : Dict[int, float]
    """

    def __init__(self, posting_type: PostingType, *args, **kwargs):
        super().__init__(posting_type)
        if posting_type not in self.allowed_posting_types:
            raise Exception(
                f'{ posting_type } not supported for {self.__class__}')
        self.documents_length = defaultdict(int)
        self.posting_class = PostingListFactory(posting_type)
    
    @staticmethod
    def load_tiny(line: str):
        return float(line)

    def load_metadata(self, metadata: Dict[str, str]):
        # check if is the same ranker, posting list, etc
        if metadata['ranker'] != 'TF_IDF':
            raise Exception(f'Ranker "{ metadata["ranker"] }" not compatible')
        if metadata['posting_class'] != 'frequency':
            raise Exception(f'Posting type "{ metadata["posting_class"] }" not compatible')

        self.metadata = metadata

    def metadata(self) -> Dict[str, object]:
        return {
            'ranker': 'TF_IDF',
            'posting_class': 'frequency'
        }

    def order(self, term_to_posting_list: Dict[str, PostingList]) -> List[Tuple[int, float]]:

        query = list(term_to_posting_list.keys())

        tfs = dict()
        for token in query:
            tfs[token] = TF_IDF_Ranker.uniform_tf(query.count(token))

        weights = tfs.values()
        sum_weights = sum([weight*weight for weight in weights])
        sqrt_weights = math.sqrt(sum_weights)

        scores: DefaultDict[int, float] = defaultdict(float)  # doc_id, score
        for term, tf in tfs.items():
            posting_list = term_to_posting_list.get(term)
            if posting_list == None: continue

            docs: List[int] = posting_list.get_documents()

            idf = posting_list.tiny
            for doc in docs:
                # query
                ltc = (tf / sqrt_weights) * idf
                # documents
                lnc = posting_list.tf_weight[doc]

                scores[doc] += ltc * lnc
        
        return sorted(scores.items(), key=lambda i: i[1], reverse=True)

    def merge_calculations(self, posting_list: PostingList):
        posting_list.idf = self.calculate_idf(posting_list)
    
    def tiny_repr(self, posting_list: PostingList):
        return str(posting_list.idf)

    def document_repr(self, posting_list: PostingList):
        return ' '.join([f'{doc_id}-{freq}/{round(posting_list.tf_weight[doc_id], 3)}' for doc_id, freq in posting_list.posting_list.items()])

    def term_repr(self, posting_list: PostingList):
        return f'{self.document_repr(posting_list)}'

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
        uniformed_tfs = TF_IDF_Ranker.uniform_weight(tfs)
        for token in tokens:
            posting_list: PostingList = term_to_postinglist[token]
            if not hasattr(posting_list, 'tf_weight'):
                TF_IDF_Ranker.posting_list_init(posting_list)
                posting_list.tf_weight[doc_id] = uniformed_tfs[token]

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
                term_frequencies[token] = TF_IDF_Ranker.uniform_tf(tokens.count(token))

        return term_frequencies

    @staticmethod
    def uniform_tf(tf):
        return 1 + math.log10(tf)

    def calculate_idf(self, posting_list: PostingList):
        return round(math.log10(len(self.documents_length)/len(posting_list.posting_list)), 3)

    @staticmethod
    def calculate_weights(tfs):
        return tfs.values()

    @staticmethod
    def uniform_weight(tfs):
        normalized_weights = {}
        weights = TF_IDF_Ranker.calculate_weights(tfs)
        sum_weights = sum([weight*weight for weight in weights])
        sqrt_weights = math.sqrt(sum_weights)

        for term, tf in tfs.items():
            normalized_weights[term] = tf / sqrt_weights

        return normalized_weights
