# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049


from collections import defaultdict
from typing import DefaultDict, Dict, List, Set, Tuple
from models.posting_list import PostingList, PostingListFactory, PostingType
from models.ranker import Ranker
import math

class TF_IDF_Ranker(Ranker):
    documents_length: DefaultDict
    allowed_posting_types = [PostingType.FREQUENCY]
    posting_class: PostingList.__class__
    schema: str
    allowed_schemas: Set[str] = [
        'nlb',
        'ntp',
        'nc'
    ]
    allowed_posting_types: Set[PostingType] = {
        PostingType.FREQUENCY
    }

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
        if 'schema' in kwargs:
            self.schema = kwargs['schema']
            TF_IDF_Ranker.validate_schema(kwargs['schema'])
        else:
            self.schema = 'lnc.ltc'


    
    @staticmethod
    def load_tiny(line: str):
        return float(line)
    
    @staticmethod
    def validate_schema(ranker_schema:str):
        valid = True
        if ranker_schema[3] != '.': error = True
        if ranker_schema[0] not in TF_IDF_Ranker.allowed_schemas[0]: valid = False
        if ranker_schema[1] not in TF_IDF_Ranker.allowed_schemas[1]: valid = False
        if ranker_schema[2] not in TF_IDF_Ranker.allowed_schemas[2]: valid = False
        if ranker_schema[4] not in TF_IDF_Ranker.allowed_schemas[0]: valid = False
        if ranker_schema[5] not in TF_IDF_Ranker.allowed_schemas[1]: valid = False
        if ranker_schema[6] not in TF_IDF_Ranker.allowed_schemas[2]: valid = False
        if not valid: raise Exception(f'Schema "{ ranker_schema }" not supported for {TF_IDF_Ranker.__class__ }')

    def load_metadata(self, metadata: Dict[str, str]):
        if metadata['ranker'] != 'TF_IDF':
            raise Exception(f'Ranker "{ metadata["ranker"] }" not compatible with {self.__class__}')
        if PostingType(metadata['ranker_posting_class']) not in self.allowed_posting_types:
            raise Exception(f'Posting type "{ metadata["ranker_posting_class"] }" not compatible with {self.__class__}')
        TF_IDF_Ranker.validate_schema(metadata['ranker_schema'])
        self.schema = metadata['ranker_schema']
        self.metadata = metadata

    def metadata(self) -> Dict[str, object]:
        return {
            'ranker': 'TF_IDF',
            'ranker_posting_class': 'frequency',
            'ranker_schema': self.schema
        }

    def order(self, query:List[str], term_to_posting_list: Dict[str, PostingList]) -> List[Tuple[int, float]]:

        tfs = dict()
        for token in term_to_posting_list.keys():
            tfs[token] = self.uniform_tf(query.count(token), self.schema[4])

        scores: DefaultDict[int, float] = defaultdict(float)  # doc_id, score

        # query
        ltc:Dict[str, float] = dict()
        for term, tf in tfs.items():
            posting_list = term_to_posting_list.get(term)
            if posting_list == None: continue

            idf = posting_list.tiny
            ltc[term] = tf * idf
        uniformed_ltc = TF_IDF_Ranker.uniform_weight(ltc, self.schema[6])

        # documents
        for term, tf in tfs.items():
            posting_list = term_to_posting_list.get(term)
            if posting_list == None: continue

            docs: List[int] = posting_list.get_documents()

            for doc in docs:
                lnc = self.calculate_idf(posting_list, self.schema[1]) * posting_list.tf_weight[doc]

                scores[doc] += lnc * uniformed_ltc[term]
        
        return sorted(scores.items(), key=lambda i: i[1], reverse=True)

    def merge_calculations(self, posting_list: PostingList):
        posting_list.idf = self.calculate_idf(posting_list, self.schema[5])
    
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
        uniformed_tfs = TF_IDF_Ranker.uniform_weight(tfs, self.schema[2])
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
                term_frequencies[token] = self.uniform_tf(tokens.count(token), self.schema[0])

        return term_frequencies

    def uniform_tf(self, tf, alg):
        if alg == 'l':
            return 1 + math.log(tf) if tf > 0 else 0
        elif alg == 'b':
            return 1 if tf > 0 else 0
        elif alg == 'n':
            return tf

    def calculate_idf(self, posting_list: PostingList, alg):
        try:
            if alg == 't':
                return round(math.log(len(self.documents_length)/len(posting_list.posting_list)), 3)
            elif alg == 'p':
                return round(max(0, math.log((len(self.documents_length)-len(posting_list.posting_list))/len(posting_list.posting_list))), 3)
            elif alg == 'n':
                return 1
        except ValueError:
            return 0

    @staticmethod
    def uniform_weight(tfs, alg):
        if alg == 'c':
            normalized_weights = {}
            weights = tfs.values()
            sum_weights = sum([weight*weight for weight in weights])
            sqrt_weights = math.sqrt(sum_weights)

            for term, tf in tfs.items():
                normalized_weights[term] = tf / sqrt_weights

            return normalized_weights
        elif alg == 'n':
            return {term: 1 for term, tf in tfs.items()}
