
from models.spimi import Spimi
from models.index import InvertedIndex
import time, os, glob
from parser import Parser
from tokenizer import Tokenizer


BLOCK_DIR = 'cache/blocks'
OUTPUT_INDEX = f'cache/index/{time.time()}.index'


def remove_blocks(block_dir:str):
    files = glob.glob(f'{block_dir}/*.block')
    for f in files:
        os.remove(f)


def main():
    remove_blocks(os.path.join(os.path.dirname(__file__), f'../{BLOCK_DIR}'))

    parser = Parser('datasets/digital_video_games.tsv', 'review_id', set(['review_headline', 'review_body']))
    tokenizer = Tokenizer(4, 'stop_words.txt', 'english')
    parsed_text = parser.parse('\t')
    indexer = Spimi(max_ram_usage=95, max_block_size=5000, auxiliary_dir=f'../../{BLOCK_DIR}')

    print("Creating documents and indexing")
    start = time.time()
    for i, (doc_id, text) in enumerate(parsed_text.items()):
        if i%1000 == 0:
            print(i)

        tokens = tokenizer.tokenize(text)
        indexer.add_document(doc_id = i, tokens=tokens)
    
    print(f"time to create blocks: {time.time()-start}")
    print("Index construction")
    start = time.time()

    index = InvertedIndex(indexer.construct_index(f'../../{OUTPUT_INDEX}'))
    print(f"time to create the main index: {time.time()-start}")


if __name__ == '__main__':
    main()