# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049

from argparse import ArgumentParser
import time
from typing import List
from models.index import InvertedIndex
from models.ranker import RankerFactory
from models.tokenizer import Tokenizer

def parse_args():
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "--search-index",
        dest="search_index",
        help="Path to the index file to search",
        required=False
    )
    arg_parser.add_argument(
        "--search-terms",
        nargs="*",
        dest="search_terms",
        help="Term to search for",
        required=False
    )
    arg_parser.add_argument(
        "--n",
        type=int,
        dest="n_results",
        help="Number of results to return in the search method",
        required=False,
        default=10
    )

    return arg_parser.parse_args()



def search(index_file:str, search_terms:List[str], n_results:int, verbose:bool=False):

        t1 = time.perf_counter()
        index = InvertedIndex(None, output_path=index_file)
        t2 = time.perf_counter()
        if verbose: print(f"Time to start searcher {(t2-t1)* 100}ms")

        ranker = RankerFactory(index.metadata['ranker'])(index.metadata['posting_class'])

        tokenizer = Tokenizer(index.metadata['min_token_length'],
                            index.metadata['stop_words'], index.metadata['language'])

        tokens = tokenizer.tokenize(" ".join(search_terms))

        t1 = time.perf_counter()

        #  get the seach result
        matches = [int(doc_id) for doc_id in index.search(tokens, n_results, ranker, show_score=False)]

        # convert the auxiliary doc id into real ones
        doc_id_to_real_doc_id = index.fetch_terms(matches, index.metadata['doc_mapping'])

        t2 = time.perf_counter()
        if verbose: print(f"Search in {(t2-t1)* 100}ms")

        return [doc_id_to_real_doc_id[match] for match in matches]


if __name__ == '__main__':
    args = parse_args()
    if args.search_terms == None:
        while(True):
            search_terms = input("Search (exit 'q'): ").split(' ')
            if len(search_terms) == 1 and search_terms[0].lower() == 'q': break
            results = search(args.search_index, search_terms, args.n_results)
            print(results)
    else:
        results = search(args.search_index, args.search_terms, args.n_results)
        print(results)
