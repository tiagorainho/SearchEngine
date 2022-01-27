# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049


from collections import defaultdict
from typing import DefaultDict, Dict, List
from models.posting_list import PostingList, PostingType
from models.ranker import RankingMethod
import math
from models.rankers.bm25 import BM25_Ranker


class BM25_Positional_Ranker(BM25_Ranker):
    k: float
    b: float
    boost_weight: float
    max_distance: int
    c: float
    documents_length: DefaultDict
    posting_class: PostingList.__class__
    allowed_posting_types = [PostingType.POSITIONAL]
    ranking_method: RankingMethod


    def __init__(self, posting_type: PostingType, *args, **kwargs):
        super().__init__(posting_type, *args, **kwargs)
        self.ranking_method = RankingMethod.BM25_OPTIMIZED
        self.boost_weight = 0.01
        self.max_distance = 10
        self.c = math.log10(self.max_distance*1.5)

    def compute_distance(self, i:int, positions1:List[int], j:int, positions2:List[int]):
        score:float = 0
        query_distance:int = j-i
        for position1 in positions1:
            max_score:int = 0
            for position2 in positions2:
                positions_distance = position2-position1
                if abs(positions_distance) > self.max_distance: continue
                signal:int = -1 if positions_distance < 0 else 1
                distance = signal*(query_distance-positions_distance)
                if distance >= 0:
                    aux_score = - math.log10(distance + 1) + self.c
                else:
                    aux_score = (math.log10(-distance + 1) + self.c )*0.8
                if aux_score > max_score: max_score = aux_score
            score += max_score
        return score

    
    def calculate_boost(self, query:List[str], doc_id:int, term_to_posting_list:Dict[str, PostingList]):
        # get positions for each term
        term_to_positions = dict()
        for term in query:
            posting_list = term_to_posting_list.get(term)
            if posting_list == None:
                term_to_positions[term] = []
            else:
                positions = posting_list.posting_list.get(doc_id, [])
                term_to_positions[term] = positions

        # calculate boost
        score = 0
        for i, term1 in enumerate(query, start=1):
            term1_positions = term_to_positions[term1]
            for j, term2 in enumerate(query[i:], start=1):
                term2_positions = term_to_positions[term2]
                if term1 == term2: continue
                score += self.compute_distance(i, term1_positions, j+i+1, term2_positions)
        return math.log10(score) if score > 0 else 0
    
    def order(self, query:List[str], term_to_posting_list: Dict[str, PostingList]) -> Dict[int, float]:
        tfs = dict()
        for token in query:
            tfs[token] = query.count(token)

        scores: DefaultDict[int, float] = defaultdict(float)  # doc_id, score
        dl_div_avgdl = self.metadata["doc_length_normalization"]
        min_dl_div_avgdl = min(self.metadata["doc_length_normalization"].values())
        max_dl_div_avgdl = max(self.metadata["doc_length_normalization"].values())

        # calculate BM25 score
        for term, tf in tfs.items():
            posting_list = term_to_posting_list.get(term)
            if posting_list != None:
                docs: List[int] = posting_list.get_documents()
                for doc in docs:
                    freq = len(posting_list.posting_list[doc])
                    idf = posting_list.tiny
                    tf = (freq * (self.k + 1)) / (freq + self.k * (1 - self.b + self.b * dl_div_avgdl[doc]))
                    scores[doc] += idf * tf

        # calculate positional boost
        for doc, bm25_score in scores.items():
            boost_score = self.calculate_boost(query, doc, term_to_posting_list)

            # normalize scores
            doc_length_normalization = math.log2((dl_div_avgdl[doc]-min_dl_div_avgdl)/(max_dl_div_avgdl-min_dl_div_avgdl)+1)
            # doc_length_normalization = math.log2(dl_div_avgdl[doc])

            # if boost_score > 0:
            #     print(doc, "bm25", bm25_score, "boost", (self.boost_weight)*boost_score/doc_length_normalization)

            scores[doc] = bm25_score + (self.boost_weight) * boost_score / doc_length_normalization

        return sorted(scores.items(), key=lambda i: i[1], reverse=True)

    def document_repr(self, posting_list: PostingList):
        return str(posting_list)

    def metadata(self) -> Dict[str, object]:
        return {
            'ranker': str(self.ranking_method).split('.')[1],
            'ranker_posting_class': 'positional',
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
        if metadata['ranker'] != str(self.ranking_method).split('.')[1]:
            raise Exception(f'Ranker "{ metadata["ranker"] }" not compatible')
        if self.k == None: self.k = float(metadata['k'])
        if self.b == None: self.b = float(metadata['b'])
        self.metadata = metadata
    
    def load_posting_list(self, line: str) -> PostingList:

        posting_list = self.posting_class()

        for posting in line.split(' '):
            doc_id, positions = tuple(posting.split(':'))
            posting_list.posting_list[doc_id] = [int(position) for position in positions.split(',')]

        return posting_list