# Authors:
# Tiago Rainho - 92984
# Vasco Sousa  - 93049

from string import ascii_letters
from efficiency import Efficiency
from models.spimi import Spimi
from models.index import InvertedIndex
import time
from models.posting_list import PostingType
from models.ranker import RankerFactory, RankingMethod
from models.tokenizer import Tokenizer
from indexer import index
import os

BLOCK_DIR = 'cache/blocks'
OUTPUT_INDEX = f'cache/index/{time.time()}.index'
DOC_MAPPING_FILE = 'cache/docs_mapping.txt'


# TOKENIZER IS NOT ACTIVE FOR THIS TESTS

if __name__ == '__main__':

    efficiency = Efficiency()
    show_efficiency = True

    os.makedirs(f"cache", exist_ok=True)
    for dir in ['blocks', 'index', 'mappings']:
        os.makedirs(f"cache/{dir}", exist_ok=True)

    stop_words = 'stop_words.txt'
    min_token_length = 0
    language = None
    # texts = ['this rock album is amazing', 'greatest rock album', 'best folk cd']
    # search_terms = "greatest rock album"
    texts = ['good games for kids', 'good old games games', 'haha lols are funny']
    search_terms = "good old games games"
    max_ram = 95
    max_block_size = 20
    posting_list_type = PostingType.FREQUENCY
    ranking_method = RankingMethod.TF_IDF
    tf_idf_schema = 'lnc.ltc'
    n_results = 3
    bm25_k = 1.2
    bm25_b = 0.75

    ranker = RankerFactory(ranking_method)(posting_list_type, schema=tf_idf_schema, k=bm25_k, b=bm25_b)

    print("------------ Indexing -------------")
    
    t1 = time.perf_counter()
    indexer = Spimi(ranker=ranker, max_ram_usage=max_ram, max_block_size=max_block_size,
                    auxiliary_dir=BLOCK_DIR, posting_type=posting_list_type)

    indexer.extend_metadata({
        'posting_class': posting_list_type.value,
        'min_token_length': min_token_length,
        'stop_words': stop_words,
        'language': language,
        'doc_mapping': DOC_MAPPING_FILE
    })

    counter:int = 0
    with open(DOC_MAPPING_FILE, 'w', encoding='utf-8') as mapping_file:

        tokenizer = Tokenizer(min_token_length, stop_words, language)
        for text in texts:
            tokens = text.split(' ') # tokenizer.tokenize(text)
            doc_id = ascii_letters[counter]
            indexer.add_document(doc_id=counter, tokens=tokens)
            mapping_file.write(f'{counter} {doc_id}\n')
            counter += 1

        index = indexer.construct_index(OUTPUT_INDEX)
    t2 = time.perf_counter()

    indexer.clear_blocks()
    print(f'whole indexing took: {t2-t1} seconds')

    print("\n------------ Searching -------------")

    t1 = time.perf_counter()
    index = InvertedIndex(None, output_path=OUTPUT_INDEX)
    t2 = time.perf_counter()
    print(f"Time to start searcher {(t2-t1)* 100}ms")

    ranker = RankerFactory(RankingMethod(index.metadata['ranker']))(PostingType(index.metadata['posting_class']))
    
    tokenizer = Tokenizer(index.metadata['min_token_length'], index.metadata['stop_words'], index.metadata['language'])
    tokens = search_terms.split(' ') # tokenizer.tokenize(search_terms)

    #  get the seach result
    t1 = time.perf_counter()
    result = index.search(tokens, n_results, ranker, show_score=True)
    t2 = time.perf_counter()

    if show_efficiency:
        efficiency.add_search_time(t2-t1)
        efficiency.calculate_stats(search_terms, result)
        print(efficiency)

    print(result)
