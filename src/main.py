from string import ascii_letters
from models.spimi import Spimi
from models.index import InvertedIndex
from models.posting import PostingType
import time
from parser import Parser
from ranker import Ranker, RankerFactory, RankingMethod
from tokenizer import Tokenizer
from argparse import ArgumentParser
import cProfile

BLOCK_DIR = 'cache/blocks'
OUTPUT_INDEX = f'cache/index/{time.time()}.index'


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
            dest="ranking_method",
            help="Ranking method to use while indexing and searching",
            required=False,
            default=None
        )
        arg_parser.add_argument(
            "--k",
            dest="bm25_k",
            help="K value for the BM25 ranking method",
            required=False,
            default=0.75
        )
        arg_parser.add_argument(
            "--b",
            dest="bm25_b",
            help="B value for the BM25 ranking method",
            required=False,
            default=0.5
        )

        self.args = arg_parser.parse_args()

    def index(self):

        ranker = None
        if self.args.ranking_method != None:
            ranker = RankerFactory(RankingMethod.BM25)(self.args.posting_list_type, 0.5, 0.75)

        indexer = Spimi(ranker=ranker, max_ram_usage=self.args.max_ram, max_block_size=self.args.max_block_size,
                    auxiliary_dir=BLOCK_DIR, posting_type=self.args.posting_list_type)

        for document in self.args.documents:
            parser = Parser(document, 'review_id', [
                            'review_headline', 'review_body'])

            tokenizer = Tokenizer(
                self.args.min_token_length, self.args.stop_words, self.args.language)

            parser_generator = parser.parse('\t')

            print(
                f"Start {str(self.args.posting_list_type).lower().replace('postingtype.','')} indexing...")

            start = time.perf_counter()
            for doc_id, parsed_text in parser_generator:
                tokens = tokenizer.tokenize(parsed_text)
                indexer.add_document(doc_id=doc_id, tokens=tokens)

            print("const begin")
            index = indexer.construct_index(OUTPUT_INDEX)
            print("const end")
            end = time.perf_counter()
            print(
                f"End file indexing {round((end-start), 3)} seconds with {indexer.block_number} temporary file{'s' if indexer.block_number != 1 else ''}")

            indexer.clear_blocks()

            return index

    def search(self):
        # ranker = None
        # if self.args.ranking_method != None:
        #     ranker = RankerFactory(self.args.ranking_method)(self.args.posting_list_type, self.args.k, self.args.b)
        ranker = RankerFactory(RankingMethod.BM25)(self.args.posting_list_type, 1.25, 0.75)
        tokenizer = Tokenizer(self.args.min_token_length,
                              self.args.stop_words, self.args.language)

        t1 = time.perf_counter()
        index = InvertedIndex(None, self.args.posting_list_type,
                              self.args.search_index)
        t2 = time.perf_counter()
        print(f"Time to start searcher {(t2-t1)* 100}ms")

        tokens = tokenizer.tokenize(" ".join(self.args.search_terms))

        print(tokens)

        t1 = time.perf_counter()
        matches = index.search(tokens, 10, ranker, True)
        t2 = time.perf_counter()
        print(f"Search in {(t2-t1)* 100}ms")
        print(f"{matches}")

    def main(self):
        if self.args.documents:
            self.index()
        elif self.args.search_index and self.args.search_terms:
            self.search()


if __name__ == '__main__':
    #cProfile.run('Main().main()')
    Main().main()

    exit(0)

    stop_words = 'stop_words.txt'
    min_token_length = 0
    language = None
    texts = ['ola bem bem, curto bue de escrever ola',
             " e tu? ta bem td fixe oi oi ola cnt", "kkk oi haha oafahfai fuah ahfa hauf uawfh a"]
    search_terms = "oi ola tudo kkk"
    max_ram = 95
    max_block_size = 2000
    posting_list_type = PostingType.FREQUENCY
    ranking_method = RankingMethod.BM25
    ranker = RankerFactory(ranking_method)(posting_list_type, 0.75, 0.5)

    print("------------ Indexing -------------")

    t1 = time.perf_counter()
    indexer = Spimi(ranker=ranker, max_ram_usage=max_ram, max_block_size=max_block_size,
                    auxiliary_dir=BLOCK_DIR, posting_type=posting_list_type)

    tokenizer = Tokenizer(min_token_length, stop_words, language)
    for i, parsed_text in enumerate(texts):
        tokens = tokenizer.tokenize(parsed_text)
        text = ascii_letters[i]

        indexer.add_document(doc_id=text, tokens=tokens)

    index = indexer.construct_index(OUTPUT_INDEX)

    t2 = time.perf_counter()
    print(index.inverted_index)

    indexer.clear_blocks()

    print(f'whole indexing took: {t2-t1} seconds')

    print("\n------------ Searching -------------")

    t1 = time.perf_counter()
    index = InvertedIndex(None, posting_list_type,
                          'cache/index/1640048848.117843.index')
    print("retrieved index: ", index.inverted_index)
    print()

    tokenizer = Tokenizer(min_token_length, stop_words, language)
    tokens = tokenizer.tokenize(search_terms)
    matches = index.search(tokens, 10, ranker, show_score=True)
    t2 = time.perf_counter()
    print(f'whole searching took: {t2-t1} seconds')
    print()
    print(f"result: {matches}")
