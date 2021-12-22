
from time import time
from models.index import InvertedIndex
from models.ranker import RankerFactory
from models.tokenizer import Tokenizer


def search(self, index:InvertedIndex=None):
    ranker = None
    if self.args.ranking_method != None:
        ranker = RankerFactory(self.args.ranking_method)(self.args.posting_list_type, k=self.args.bm25_k, b=self.args.bm25_b)

    tokenizer = Tokenizer(self.args.min_token_length,
                            self.args.stop_words, self.args.language)

    tokens = tokenizer.tokenize(" ".join(self.args.search_terms))

    t1 = time.perf_counter()
    matches = index.search(tokens, self.args.n_results, ranker, show_score=False)
    t2 = time.perf_counter()
    print(f"Search in {(t2-t1)* 100}ms")
    print(f"{matches}")

if __name__ == '__main__':
    pass