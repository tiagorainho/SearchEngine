from typing import List
from models.spimi import Spimi
from indexer import Indexer


class Cluster:
    partitions:int = 3 # number of inverters
    parserWorkers: int = 3

    def __init__(self):
        pass


    def update(files:List[str]):
        pass


    def _map(self):
        pass


    def _reduce(self):
        pass


if __name__ == "__main__":

    indexer = Indexer(Spimi, 1000)

    indexer.load_from_disk()

    split_docs = []

    cluster = Cluster()

