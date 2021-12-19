from io import FileIO
from typing import Dict, Generator, List, Tuple
from models.index import InvertedIndex
from models.posting import PostingType
from models.posting_list import PostingList, PostingListFactory
from ranker import Ranker, RankerFactory, RankingMethod
from pathlib import Path
import threading
import psutil
import heapq
import os
import glob

class Spimi():
    AUXILIARY_DIR: str
    BLOCK_SUFFIX: str = 'block'
    MAX_BLOCK_SIZE: int
    MAX_RAM_USAGE: int
    block_number: int
    inverted_index: InvertedIndex
    posting_list_class: PostingList
    posting_type: PostingType
    ranker: Ranker
    ram_usage: float
    can_update_ram: threading.Event
    document_done: threading.Event

    def __init__(self, max_ram_usage: int = 85, max_block_size: int = 10000, auxiliary_dir: str = 'cache/blocks', posting_type: PostingType = PostingType.FREQUENCY, ranking_method:RankingMethod=RankingMethod.TF_IDF) -> None:
        """
        Creates a new instance of a SPIMI indexer, this is used to create indexes and initialize static variables

        :return: None
        """
        self.MAX_BLOCK_SIZE = max_block_size
        self.MAX_RAM_USAGE = max_ram_usage
        self.AUXILIARY_DIR = auxiliary_dir
        self.block_number = 0
        self.inverted_index = InvertedIndex(dict(), posting_type)
        self.posting_type = posting_type
        self.posting_list_class = PostingListFactory(posting_type)
        self.ranker = RankerFactory(ranking_method)(posting_type)

        self.ram_usage = self.get_ram_usage()
        self.can_update_ram = threading.Event()
        self.document_done = threading.Event()
        self.document_done.set()
        self.can_update_ram.set()
        thread = threading.Thread(target=self.update_ram, daemon=True)
        thread.start()
        
         
    def get_ram_usage(self):
        return psutil.virtual_memory().percent

    def update_ram(self):
        while True:
            self.can_update_ram.wait()
            self.document_done.clear()
            self.ram_usage = self.get_ram_usage()
            self.document_done.set()

    def add_document(self, doc_id: int, tokens: List[str]) -> None:
        """
        Add a new document to be indexed. The indexing takes into account memory usage and created index size

        :param doc_id: document ID
        :param tokens: list of tokens from the document
        :return: None
        """
        self.can_update_ram.set()

        self.ranker.before_add_tokens(self.inverted_index.inverted_index, tokens, doc_id)
        self.inverted_index.add_tokens(tokens, doc_id)
        self.ranker.after_add_tokens(self.inverted_index.inverted_index, tokens, doc_id)

        self.can_update_ram.clear()
        self.document_done.wait()

        if(self._inverted_index_size >= self.MAX_BLOCK_SIZE or self.ram_usage >= self.MAX_RAM_USAGE):
            self._write_block_to_disk(f"{self.AUXILIARY_DIR}/{self.block_number}.{self.BLOCK_SUFFIX}")
            self.inverted_index.clear()

    @property
    def _inverted_index_size(self) -> int:
        """
        Return the size of the inverted index

        :return: integer
        """
        return len(self.inverted_index.inverted_index)

    def _write_block_to_disk(self, output_path: str) -> None:
        """
        Write an inverted index to a given file

        :param output_file: file to write the index
        :return: None
        """
        self.inverted_index.save(Path(output_path).resolve(), self.ranker)
        self.block_number += 1

    def get_lines_from_block(self, file: FileIO) -> List[str]:
        """
        reads lines from a file IO based on the MAX_USAGE_BLOCK variable

        :param file: file io which means it is already opened
        :return: list of at most MAX_USAGE_BLOCK strings read by the file, otherwise divide the MAX_USAGE_BLOCK by the number of blocks to read
        """
        return [file.readline().replace('\n', '') for _ in range(int(self.MAX_BLOCK_SIZE/self.block_number))]

    def load_line(self, line) -> Tuple[str, PostingList]:
        """
        Parses the term and posting list from a line of text

        :param line: line to be parsed
        :return: Tuple of term and PostingList
        """
        return self.inverted_index.load(line, self.ranker)

    def file_generator(self, file: str) -> Generator[List[str], None, None]:
        """
        Abstracts the lines access of the given file as a generator. When it is done, closes the file access

        :param file: file from which to read the lines
        :return: list of strings
        """
        file_io = open(file)
        while True:
            lines = [line for line in self.get_lines_from_block(
                file_io) if line != '']
            if lines == []:
                break
            yield lines
        file_io.close()

    def min_k_merge_generator(self, files: List[str]) -> Generator[Tuple[str, PostingList], None, None]:
        """
        Provide an abstraction to get the minimum term of a set of files. The abstraction choosen was the generator abstraction. The sorting proccess is fast because already done comparisons dont go to waste as it forms a tree data structure

        :param files: list of files from which to get the values
        :return: a tuple with the mininum valued term and its posting lists as it comes in the files
        """
        generators = [(file, self.file_generator(file)) for file in files]

        # generators buffer
        lines_buffer = []
        for generator in generators:
            try:
                lines = next(generator[1])
                lines_buffer.append(lines)
            except StopIteration:
                pass

        # create heap
        heap: List[Node] = []
        for i, line in enumerate(lines_buffer):
            first_line = line.pop(0)
            first_term, first_posting_list = self.load_line(first_line)
            heap.append(Node(first_term, first_posting_list, i))
        heapq.heapify(heap)

        # merge documents until there is none left
        while len(heap) > 0:
            smallest_node = heapq.heappop(heap)
            smallest_nodes = [smallest_node]

            # add the rest of postings of the same term but different blocks
            while len(heap) > 0:
                node = heap[0]
                if node.term == smallest_node.term:
                    smallest_nodes.append(heapq.heappop(heap))
                else:
                    break

            # merge posting lists from different blocks and yield the result
            merged_posting_list = self.posting_list_class.merge(
                [smallest_node.posting_list for smallest_node in smallest_nodes])
            yield (smallest_node.term, merged_posting_list)

            for node in smallest_nodes:
                # repopulate lines_buffer when is empty
                buffer = lines_buffer[node.block_id]
                if buffer == []:
                    try:
                        lines = next(generators[node.block_id][1])
                        lines_buffer[node.block_id].extend(lines)
                    except StopIteration:
                        pass

                # repopulate heap
                if lines_buffer[node.block_id] != []:
                    line = lines_buffer[node.block_id].pop(0)
                    term, posting_list = self.load_line(line)
                    heapq.heappush(heap, Node(
                        term, posting_list, node.block_id))

    def _merge_blocks(self, input_paths: List[str], output_path: str):
        """
        Merge the blocks which are "mini" indexes and transform them into one larger index

        :param input_files: input files from which to retrieve the "mini" indexes
        :param output_path: the file to which write the final big index
        :return: dictionary with all the terms inserted in the final index
        """
        min_term_generator = self.min_k_merge_generator(input_paths)
        index: Dict[str, None] = dict()

        with open(Path(output_path).resolve(), 'w') as output_file:
            # get mininum terms and their respective posting list
            for term, posting_list in min_term_generator:
                output_file.write(f"{term} {self.ranker.term_repr(posting_list)}\n")
                index[term] = posting_list # None    # DEIXAR NONE -------------------------------------------------------------------------------------------------------------------

        return InvertedIndex(index, self.posting_type, output_path)

    def construct_index(self, ouput_path: str = 'output.index'):
        """
        Construct an index from multiple indexes and write that index to a new file

        :param posting_list_dir: file to which output the result index
        :return: dictionary with only the terms as keys and None as values because the management of the index is done by the InvertedIndex class
        """
        # add last block
        if self._inverted_index_size > 0:
            self._write_block_to_disk(
                f"{self.AUXILIARY_DIR}/{self.block_number}.{self.BLOCK_SUFFIX}")

        # get all files from the postings directory
        block_paths = Path("cache/blocks").rglob(f"*{self.BLOCK_SUFFIX}")
        input_paths = [Path(file).resolve() for file in block_paths]

        # merge those blocks into one file
        index = self._merge_blocks(input_paths, ouput_path)

        return index

    def clear_blocks(self):
        for f in glob.glob(f'cache/blocks/*.block'):
            os.remove(f)


class Node:
    """
    Node of the heap used in the min_k_merge_generator() to sort the values with O(logN) complexity
    """
    term: str
    posting_list: PostingList
    block_id: int

    def __init__(self, term: str, posting_list: PostingList, block_id: int):
        self.term = term
        self.posting_list = posting_list
        self.block_id = block_id

    def __lt__(self, other):
        return self.term < other.term
