
from typing import Generator, List, Tuple
from models.spimi2 import Spimi
from models.index import InvertedIndex
import random, string, time, os, glob


BLOCK_DIR = 'cache/blocks'
OUTPUT_INDEX = f'cache/index/{time.time()}.index'


def remove_blocks(block_dir:str):
    files = glob.glob(f'{block_dir}/*.block')
    for f in files:
        os.remove(f)


def create_docs(number_of_docs:int, review_length:int, possible_tokens_len:int=50, max_token_size:int=8) -> Generator[List[Tuple[int, List[str]]], None, None]:
    #possible_tokens = [''.join(random.choices(string.ascii_lowercase)) for _ in range(tokens_length)] # only one char tokens
    possible_tokens = [''.join(random.choices(string.ascii_lowercase, k = random.randrange(1, max_token_size))) for token in range(possible_tokens_len)]
    for _ in range(number_of_docs):
        doc_id = random.randrange(0, number_of_docs)
        tokens = [possible_tokens[random.randrange(0, len(possible_tokens))] for _ in range(review_length)]
        yield (doc_id, tokens)


def main():
    random.seed(100)

    # remove blocks for easier understanding of the generated blocks
    remove_blocks(os.path.join(os.path.dirname(__file__), f'../{BLOCK_DIR}'))

    indexer = Spimi(max_ram_usage=95, max_block_size=10000, auxiliary_dir=f'../../{BLOCK_DIR}')

    #indexer.add_document(doc_id=1, tokens=["bem", "tudo", "sou"])
    #indexer.add_document(doc_id=2, tokens=["tiago", "bem", "chamo-me", "oi", "eu", "bem","o", "tiago", "bem"])

    doc_generator = create_docs(number_of_docs=1000, review_length=70, possible_tokens_len=280000)
    print("Creating documents and indexing")
    start = time.time()
    for i, (doc_id, tokens) in enumerate(doc_generator):
        if i % 1000 == 0:
            print(i)
        indexer.add_document(doc_id = doc_id, tokens=tokens)
    print(f"time to create blocks: {time.time()-start}")
    print("Index construction")
    start = time.time()
    index = InvertedIndex(indexer.construct_index(f'../../{OUTPUT_INDEX}'))
    print(f"time to create the main index: {time.time()-start}")

    #print(index)


if __name__ == '__main__':
    main()