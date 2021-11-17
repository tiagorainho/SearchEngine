
from io import TextIOWrapper
from models.spimi import Spimi
from models.index import InvertedIndex
from models.posting import PostingType
import time, os, glob
from parser import Parser
from tokenizer import Tokenizer

import cProfile # test


BLOCK_DIR = 'cache/blocks'
OUTPUT_INDEX = f'cache/index/{time.time()}.index'


def remove_blocks(block_dir:str):
    files = glob.glob(f'{block_dir}/*.block')
    for f in files:
        os.remove(f)


def generate_index() -> InvertedIndex:
    # remove old blocks for better understanding of the blocks folder
    remove_blocks(os.path.join(os.path.dirname(__file__), f'../{BLOCK_DIR}'))

    parser = Parser('datasets/digital_video_games.tsv', 'review_id', set(['review_headline', 'review_body']))
    tokenizer = Tokenizer(4, 'stop_words.txt', 'english')
    parsed_text = parser.parse('\t')
    indexer = Spimi(max_ram_usage=95, max_block_size=50000, auxiliary_dir=f'../../{BLOCK_DIR}', posting_type=PostingType.FREQUENCY)

    print("Creating documents and indexing")
    start = time.time()
    for i,doc_id in enumerate(sorted([key for key in parsed_text.keys()])):
        tokens = tokenizer.tokenize(parsed_text[doc_id])
        indexer.add_document(doc_id = i, tokens=tokens)
        if i >= 10000:
            break
    print(f"time to create blocks: {time.time()-start}")


    print("Index construction")
    start = time.time()
    index:InvertedIndex = indexer.construct_index(f'../../{OUTPUT_INDEX}')
    print(f"time to create the main index: {time.time()-start}")
    return index



def main():
    index:InvertedIndex = generate_index()
    while True:
        query = input("Query: ")
        documents = index.light_search(query.split(' '))
        print(documents)
    
    


if __name__ == '__main__':
    #cProfile.run('main()')
    #main()
    f:TextIOWrapper = open("src/a.txt", "r")

    f.seek(0,2)
    print(f.tell())


    f.close()