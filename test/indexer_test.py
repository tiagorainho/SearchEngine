
from src.models.spimi import Spimi


def test():
    index = Spimi()
    index.add(1, ["ola", "tudo", "bem", "Antonio"], 0)
    index.add(1, ["como", "estas", "?"], 4)
    index.add(2, ["Sou", "o", "Tiago"], 0)

    assert index.inverted_index['Tiago'][0].doc_id == 2
