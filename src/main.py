from tokenizer import Tokenizer
from inverted_index import InvertedIndex
from indexer import Indexer
from argparse import ArgumentParser

indexer = Indexer()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--path", metavar="path", type=str,
                        help="New file's path to build index")
    parser.add_argument("--docId", metavar="docId", type=str,
                        help="Csv column that uniquely identify a document")
    parser.add_argument("--columns", metavar="columns",
                        help="Csv columns that belong to a document")
    return parser.parse_args()


(path, docId, columns) = parse_args()

if (path, docId, columns) != (None, None, None):
    index = InvertedIndex()
    index.add(Tokenizer(path, docId, columns))
    indexer.add(index)
