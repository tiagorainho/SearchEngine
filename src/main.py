# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049

from string import ascii_letters
from models.spimi import Spimi
from models.index import InvertedIndex
import time
from models.posting_list import PostingType
from models.parser import Parser
from models.ranker import RankerFactory, RankingMethod
from models.tokenizer import Tokenizer
from argparse import ArgumentParser

BLOCK_DIR = 'cache/blocks'
OUTPUT_INDEX = f'cache/index/{time.time()}.index'
DOC_MAPPING_FILE = 'cache/docs_mapping.txt'


class Main:

    def __init__(self) -> None:
        arg_parser = ArgumentParser()
        arg_parser.add_argument(
            "--stop-words",
            default=None,
            dest="stop_words",
            help="Path to a file that contains a list of stop words",
            required=False
        )
        arg_parser.add_argument(
            "--min-token-length",
            default=0,
            type=int,
            dest="min_token_length",
            help="Minimium number of chars that a token must have to be indexed",
            required=False
        )
        arg_parser.add_argument(
            "--language",
            type=str,
            default=None,
            dest="language",
            help="Language of the documents, needed to apply snow_stemmer",
            required=False
        )
        arg_parser.add_argument(
            "--documents",
            nargs="*",
            dest="documents",
            help="List of paths to the .gz documents that are going to be indexed",
            required=False
        )
        arg_parser.add_argument(
            "--search-index",
            dest="search_index",
            help="Path to the index file to search",
            required=False
        )
        arg_parser.add_argument(
            "--posting-list-type",
            dest="posting_list_type",
            type=PostingType,
            default=PostingType.FREQUENCY,
            help="Type of posting list to be used inside the indexer, can be either 'boolean', 'frequency' or 'positional'",
            required=False
        )
        arg_parser.add_argument(
            "--max-block-size",
            dest="max_block_size",
            type=int,
            default=50000,
            help="Maximum number of terms inside each temporary block",
            required=False
        )
        arg_parser.add_argument(
            "--max-ram",
            dest="max_ram",
            type=int,
            default=95,
            help="Maximum amount of ram usage permited before writting temporary files",
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
            "--ranker",
            type=RankingMethod,
            dest="ranking_method",
            help="Ranking method to use while indexing and searching",
            required=False,
            default=None
        )
        arg_parser.add_argument(
            "--k",
            type=float,
            dest="bm25_k",
            help="K value for the BM25 ranking method",
            required=False,
            default=0.75
        )
        arg_parser.add_argument(
            "--b",
            type=float,
            dest="bm25_b",
            help="B value for the BM25 ranking method",
            required=False,
            default=0.5
        )
        arg_parser.add_argument(
            "--n",
            type=int,
            dest="n_results",
            help="Number of results to return in the search method",
            required=False,
            default=10
        )

        self.args = arg_parser.parse_args()


    def index(self):

        ranker = None
        if self.args.ranking_method != None:
            ranker = RankerFactory(self.args.ranking_method)(self.args.posting_list_type, k=1.25, b=0.75)

        indexer = Spimi(ranker=ranker, max_ram_usage=self.args.max_ram, max_block_size=self.args.max_block_size,
                    auxiliary_dir=BLOCK_DIR, posting_type=self.args.posting_list_type)

        tokenizer = Tokenizer(self.args.min_token_length, self.args.stop_words, self.args.language)

        with open(DOC_MAPPING_FILE, 'w', encoding='utf-8') as mapping_file:

            for document in self.args.documents:
                parser = Parser(document, 'review_id', ['review_headline', 'review_body'])
                parser_generator = parser.parse('\t')

                print(f"Start {str(self.args.posting_list_type).lower().replace('postingtype.','')} indexing...")
                
                start = time.perf_counter()
                for i, (doc_id, parsed_text) in enumerate(parser_generator):
                    tokens = tokenizer.tokenize(parsed_text)
                    indexer.add_document(doc_id=i, tokens=tokens)
                    mapping_file.write(f'{i} {doc_id}\n')
                    
                index = indexer.construct_index(OUTPUT_INDEX)
                end = time.perf_counter()
                print(
                    f"End file indexing {round((end-start), 3)} seconds with {indexer.block_number} temporary file{'s' if indexer.block_number != 1 else ''}")

                indexer.clear_blocks()

        return index


    def search(self, index:InvertedIndex=None):
        ranker = None
        if self.args.ranking_method != None:
            ranker = RankerFactory(self.args.ranking_method)(self.args.posting_list_type)

        tokenizer = Tokenizer(self.args.min_token_length,
                            self.args.stop_words, self.args.language)

        tokens = tokenizer.tokenize(" ".join(self.args.search_terms))

        t1 = time.perf_counter()

        #  get the seach result
        matches = [int(doc_id) for doc_id in index.search(tokens, self.args.n_results, ranker, show_score=False)]

        # convert the auxiliary doc id into real ones
        doc_id_to_real_doc_id = index.fetch_terms(matches, DOC_MAPPING_FILE)
        matches_real_doc_id = [doc_id_to_real_doc_id[match] for match in matches]

        t2 = time.perf_counter()
        print(f"Search in {(t2-t1)* 100}ms")


        print(f"final: {matches_real_doc_id}")

    def main(self):
        if self.args.documents:
            index = self.index()
        if self.args.search_index:
            t1 = time.perf_counter()
            index = InvertedIndex(None, self.args.posting_list_type,
                                self.args.search_index)
            t2 = time.perf_counter()
            print(f"Time to start searcher {(t2-t1)* 100}ms")
        if self.args.search_terms:
            self.search(index)


if __name__ == '__main__':
    Main().main()
