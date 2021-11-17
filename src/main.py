from models.spimi import Spimi
from models.index import InvertedIndex
from models.posting import PostingType
import time
from parser import Parser
from tokenizer import Tokenizer
from argparse import ArgumentParser

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
            "--search-terms",
            nargs="*",
            dest="search_terms",
            help="Term to search for",
            required=False
        )
        self.args = arg_parser.parse_args()

    def index(self):
        for document in self.args.documents:
            print("Parsing files")
            parser = Parser(document, 'review_id', set(
                ['review_headline', 'review_body']))
            tokenizer = Tokenizer(
                self.args.min_token_length, self.args.stop_words, self.args.language)
            parsed_text = parser.parse('\t')
            indexer = Spimi(max_ram_usage=95, max_block_size=50000,
                            auxiliary_dir=BLOCK_DIR, posting_type=PostingType.BOOLEAN)

            print("Creating documents and indexing")
            start = time.time()

            for i, doc_id in enumerate(sorted([key for key in parsed_text.keys()])):
                tokens = tokenizer.tokenize(parsed_text[doc_id])
                indexer.add_document(doc_id=i, tokens=tokens)

            print(f"Time to create blocks: {time.time()-start}")

            print("Index construction")
            start = time.time()
            index = indexer.construct_index(OUTPUT_INDEX)
            indexer.clear_blocks()
            print(f"Time to create the main index: {time.time()-start}")

            return index

    def search(self):
        tokenizer = Tokenizer(self.args.min_token_length,
                              self.args.stop_words, self.args.language)
        index = InvertedIndex(None, PostingType.FREQUENCY,
                              self.args.search_index)

        tokens = tokenizer.tokenize(" ".join(self.args.search_terms))

        t1 = time.perf_counter()
        matches_light = index.light_search(tokens)
        t2 = time.perf_counter()

        print(f"{matches_light}")
        print(f"Search in {(t2-t1)* 100}ms")

    def main(self):
        if self.args.documents:
            self.index()
        elif self.args.search_index and self.args.search_terms:
            self.search()


if __name__ == '__main__':
    Main().main()
