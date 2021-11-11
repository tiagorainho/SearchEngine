
from typing import List, Tuple
from models.spimi import Spimi
from models.index import InvertedIndex
import random, string, time, os, glob


BLOCK_DIR = 'cache/blocks'
OUTPUT_INDEX = f'cache/index/{time.time()}.index'


def remove_blocks(block_dir:str):
    files = glob.glob(f'{block_dir}/*.block')
    for f in files:
        os.remove(f)


def create_docs(number_of_docs:int, tokens_length:int, max_token_size:int=10):
    #possible_tokens = [''.join(random.choices(string.ascii_lowercase)) for _ in range(tokens_length)] # only one char tokens
    possible_tokens = [''.join(random.choices(string.ascii_lowercase, k = random.randrange(1, max_token_size))) for token in range(int(tokens_length*number_of_docs/2))]
    docs: List[Tuple[int, List[str]]] = []
    for _ in range(number_of_docs):
        doc_id = random.randrange(0, number_of_docs)
        tokens = [possible_tokens[random.randrange(0, len(possible_tokens))] for _ in range(tokens_length)]
        docs.append((doc_id, tokens))
    return docs


def main():
    # remove blocks for easier understanding of the generated blocks
    remove_blocks(os.path.join(os.path.dirname(__file__), f'../{BLOCK_DIR}'))

    indexer = Spimi(max_ram_usage=98, max_block_size=20, auxiliary_dir=f'../../{BLOCK_DIR}')

    #indexer.add_document(doc_id=1, tokens=["bem", "tudo", "sou"])
    #indexer.add_document(doc_id=2, tokens=["tiago", "bem", "chamo-me", "oi", "eu", "bem","o", "tiago", "bem"])

    for doc_id, tokens in create_docs(number_of_docs=10, tokens_length=20):
        indexer.add_document(doc_id = doc_id, tokens=tokens)
    index = InvertedIndex(indexer.construct_index(f'../../{OUTPUT_INDEX}'), [f'../../{OUTPUT_INDEX}'])

    #print(index)


if __name__ == '__main__':
    main()