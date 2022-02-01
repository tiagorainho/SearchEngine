import math
from statistics import mean, median
from typing import Dict, List, Tuple
from models.index import InvertedIndex
from models.posting_list import PostingType
from models.ranker import RankerFactory, RankingMethod
from models.tokenizer import Tokenizer
import time


class Efficiency:
    precisions: Dict[str, float]
    recalls: Dict[str, float]
    ndcg: Dict[str, float]
    search_times: List[float]
    reference_results: Dict[str, List[Tuple[str, str]]]
    counter: int

    def __init__(self) -> None:
        self.precisions = dict()
        self.recalls = dict()
        self.fscores = dict()
        self.search_times = []
        self.reference_results = dict()
        self.ndcg = dict()
        self.counter = 0

        current_query = ''
        with open("queries.relevance.txt") as file:
            for line in file:
                if "Q:" in line:
                    current_query = line.split(":")[1].strip()
                    self.reference_results[current_query] = list()
                elif line.strip() == "":
                    continue
                else:
                    [doc_id, score] = line.strip().split("\t")
                    self.reference_results[current_query].append(
                        (doc_id, score))

    def query_thoughput(self):
        return self.counter / sum(self.search_times)

    def calculate_stats(self, query: str, results: List[Tuple[str, float]]):
        self.counter += len(results)

        reference = self.reference_results.get(query)
        if reference == None:
            return
        relevant_docs_n = 0

        for doc_id, score in results:
            if doc_id in list(map(lambda r: r[0], reference)):
                relevant_docs_n += 1

        recall = relevant_docs_n / (len(reference))
        precision = relevant_docs_n / len(results)
        f_score = 0
        if recall + precision > 0:
            f_score = 2 * (precision * recall) / (precision + recall)

        self.precisions[query] = precision
        self.recalls[query] = recall
        self.fscores[query] = f_score
        dcg = 0
        idcg = 0

        for i, (_, score) in enumerate(results):
            numerator = 2**score - 1
            denominator = math.log2(i + 2)
            dcg += numerator/denominator

        for i, (_, score) in enumerate(self.reference_results[query]):
            numerator = 2**float(score) - 1
            denominator = math.log2(i + 2)
            idcg += numerator/denominator

        self.ndcg[query] = dcg / idcg

    def calculate_average_precision(self):
        return mean(self.precisions.values())

    def calculate_median_query_lentency(self):
        return median(self.search_times)

    def add_search_time(self, search_time: float):
        self.search_times.append(search_time)

    def __str__(self):
        return f'precision: {self.precisions}\nrecall: {self.recalls}\nfscore: {self.fscores}\nquery_thoughput: {self.query_thoughput()}\nndcg: {self.ndcg}'



if __name__ == '__main__':
    from searcher import search
    verbose = False
    search_index = 'cache/index/bm25_optimized.index'
    n_results = [10]
    queries = [
        'greatest rock album',
        'best live performance',
        'christmas songs',
        'balkan music',
        'worst buy',
        "70's country music",
        'one hit wonder',
        'most underrated',
        'several instruments',
        'abbey road studios',
        'easy listening',
        'great cover art',
        'house party songs'
    ]

    index = InvertedIndex(None, output_path=search_index)
    ranker = RankerFactory(RankingMethod(index.metadata['ranker']))(PostingType(index.metadata['posting_class']))
    tokenizer = Tokenizer(index.metadata['min_token_length'], index.metadata['stop_words'], index.metadata['language'])

    efficiency = Efficiency()
    t1 = time.perf_counter()
    precision_sum = 0
    search_times_sum = 0
    fscores_sum = 0
    ndcg_sum = 0
    recalls_sum = 0
    total_combinations = len(queries)*len(n_results)
    for query in queries:
        for n in n_results:
            start_time = time.perf_counter()
            results = search(index, ranker, tokenizer, query.split(' '), n)
            efficiency.add_search_time(time.perf_counter()-start_time)
            efficiency.calculate_stats(query, results)

    for query in queries:
        precision_sum += efficiency.precisions[query]
        fscores_sum += efficiency.fscores[query]
        ndcg_sum += efficiency.ndcg[query]
        recalls_sum += efficiency.recalls[query]
            
    print(search_index)
    print(f"mean precision: {round(precision_sum*100/total_combinations, 3)} %")
    print(f"mean recall: {round(recalls_sum*100/total_combinations, 3)} %")
    print(f"mean query thoughput: {round(efficiency.query_thoughput(), 3)}")
    print(f"mean search times: {round(sum(efficiency.search_times)/total_combinations, 3)} s")
    print(f"mean fscore: {round(fscores_sum/total_combinations, 5)}")
    print(f"mean ndcg: {round(ndcg_sum/total_combinations, 5)}")
    print(f'total test time { round(time.perf_counter() - t1, 3) } s')