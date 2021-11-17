
from io import TextIOWrapper
from models.spimi import Spimi
from models.index import InvertedIndex
from models.posting import PostingType
import time
import os
import glob
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
            help="List of paths to the documents that are going to be indexed",
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
            print(f"Time to create the main index: {time.time()-start}")
            return index

    def search(self):
        index = InvertedIndex(None, PostingType.FREQUENCY,
                              self.args.search_index)

        t1 = time.perf_counter()
        matches = index.light_search(self.args.search_terms)
        t2 = time.perf_counter()
        print(matches)

        print(f"{(t2-t1)* 100}ms")

    def main(self):
        if self.args.documents:
            self.index()
        elif self.args.search_index and self.args.search_terms:
            self.search()


def remove_blocks(block_dir: str):
    files = glob.glob(f'{block_dir}/*.block')
    for f in files:
        os.remove(f)


if __name__ == '__main__':
    Main().main()
