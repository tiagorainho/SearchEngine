# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049


import time
from models.parser import Parser
from models.ranker import RankerFactory,RankingMethod
from models.posting_list import PostingType
from models.spimi import Spimi
from models.tokenizer import Tokenizer
from argparse import ArgumentParser

BLOCK_DIR = 'cache/blocks'
OUTPUT_INDEX = f'cache/index/{time.time()}.index'
DOC_MAPPING_FILE = 'cache/docs_mapping.txt'


def index(stop_words,min_token_length,language,documents,posting_list_type,max_block_size,max_ram,ranking_method,bm25_k,bm25_b):
    ranker = None
    if ranking_method != None:
        ranker = RankerFactory(ranking_method)(posting_list_type, k=bm25_k, b=bm25_b)

    indexer = Spimi(ranker=ranker, max_ram_usage=max_ram, max_block_size=max_block_size,
                auxiliary_dir=BLOCK_DIR, posting_type=posting_list_type)
    
    indexer.extend_metadata({
        'posting_class': posting_list_type.value,
        'min_token_length': min_token_length,
        'stop_words': stop_words,
        'language': language,
        'doc_mapping': DOC_MAPPING_FILE
    })

    tokenizer = Tokenizer(min_token_length, stop_words, language)

    with open(DOC_MAPPING_FILE, 'w', encoding='utf-8') as mapping_file:

        for document in documents:
            parser = Parser(document, 'review_id', ['review_headline', 'review_body'])
            parser_generator = parser.parse('\t')

            print(f"Start {str(posting_list_type).lower().replace('postingtype.','')} indexing...")
            
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

def parse_args():
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
    return arg_parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    index(args.stop_words,args.min_token_length,args.language,args.documents,args.posting_list_type,args.max_block_size,args.max_ram,args.ranking_method,args.bm25_k,args.bm25_b)