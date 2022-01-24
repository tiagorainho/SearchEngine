import math
from pickletools import read_uint1
import re
from statistics import mean, median
from typing import Dict, List, Tuple


class Efficiency:
    precisions: Dict[str, float]
    recalls: Dict[str, float]
    ndcg: Dict[str, float]
    search_times: List[float]
    reference_results: Dict[str, List[Tuple[str, str]]]

    def __init__(self) -> None:
        self.precisions = dict()
        self.recalls = dict()
        self.fscores = dict()
        self.search_times = []
        self.reference_results = dict()

        current_query = ''
        with open("queries.relevance.txt") as file:
            for line in file:
                if "Q:" in line:
                    current_query = line.split(":")[1].strip()
                    self.reference_results[current_query] = dict()
                elif line.strip() == "":
                    continue
                else:
                    [doc_id, score] = line.strip().split("\t")
                    self.reference_results[current_query].append(
                        (doc_id, score))

    def calculate_stats(self, query: str, results: List[Tuple[str, float]]):
        reference = self.reference_results[query]
        relevant_docs_n = 0

        for result in results:
            if result in list(map(lambda r: r[0], reference)):
                relevant_docs_n += 1

        recall = relevant_docs_n / len(reference)
        precision = relevant_docs_n / len(result)
        f_score = 2 * (precision * recall) / (precision + recall)

        self.precisions[query] = precision
        self.recalls[query] = recall
        self.fscores[query] = f_score
        dcg = 0
        idcg = 0

        for i, (_, score) in results:
            numerator = 2**score - 1
            denominator = math.log2(i + 2)
            dcg += numerator/denominator

        for i, (_, score) in self.reference_results[query]:
            numerator = 2**score - 1
            denominator = math.log2(i + 2)
            idcg += numerator/denominator

        self.ndcg = dcg / idcg

    def calculate_average_precision(self):
        return mean(self.precisions.values())

    def calculate_median_query_lentency(self):
        return median(self.search_times)

    def add_search_time(self, search_time: float):
        self.search_times.append(search_time)

    def __str__(self):
        return f'{self.precisions}\n{self.recalls}\n{self.fscores}'
