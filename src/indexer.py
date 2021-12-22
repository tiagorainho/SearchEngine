
from time import time
from models.parser import Parser
from models.ranker import Ranker
from models.spimi import Spimi
from models.tokenizer import Tokenizer


def index(self, BLOCK_DIR, OUTPUT_INDEX):

    ranker = None
    if self.args.ranking_method != None:
        ranker = Ranker(self.args.ranking_method)(self.args.posting_list_type, k=1.25, b=0.75)

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

        index = indexer.construct_index(OUTPUT_INDEX)
        end = time.perf_counter()
        print(
            f"End file indexing {round((end-start), 3)} seconds with {indexer.block_number} temporary file{'s' if indexer.block_number != 1 else ''}")

        indexer.clear_blocks()

        return index


if __name__ == '__main__':
    pass