from inverted_index import InvertedIndex

index = InvertedIndex()
index.add("test", 2)
index.add("test", 1)
index.add("another", 1)

assert index.search("test") == [2, 1]
assert index.search("another") == [1]
