# Search Engine

## Motivation

When there is a need to search terms from multiple large documents, inevitably the problem of long delays during fetching of documents from a list of terms will occur, this project aims to speed up that process while increasing other measures of quality in the process by indexing the *text corpus*.

## Why

This project is an **Information Retrieval** assignment and will be composed by 3 different steps:
- [x] Parser, Tokenizer, Indexer steps and light searcher
- [ ] Complex Searcher
- [ ] Other

## Install dependencies

Download the code
```
# https
https://github.com/tiagorainho/SearchEngine.git

# ssh
git@github.com:tiagorainho/SearchEngine.git

# zip
https://github.com/tiagorainho/SearchEngine/archive/refs/heads/main.zip
```

Create virtual environment and activate it
```
python3 -m venv venv
source venv/bin/activate
```
Install dependencies
```
pip install -r requirements.txt
```

## How to use

Create the index
```
python3 src/main.py --stop-words stop_words.txt --min-token-length 3 --language english --max-block-size 50000 --max-ram 95 --posting-list-type positional --documents datasets/example.csv
```
Search in the index
```
python3 src/main.py --search-index cache/index/index_file.index --posting-list-type positional --search-terms good to know you
```


## Content

The following classes and their hierarchical structure are the following:
- [Parser](#parser)
- [Tokenizer Index](#tokenizer)
- [Indexer](#indexer)
    - [SPIMI (Single Pass In Memory Indexing)](#spimi-single-pass-in-memory-indexing)
- [Inverted Index](#inverted-index)
    - [Boolean Posting List](#boolean-posting-list)
    - [Frequency Posting List](#frequency-posting-list)
    - [Positional Posting List](#positional-posting-list)


## In depth

In this section, a more in depth look will be taken into each class.

### Parser

In order to decrease cache misses in a large list and also to better management of RAM (Random Access Memory), the ``parse()`` function does not return a list of parsed texts, instead it yields the parsed text in chuncks. This did **not** improve the performance of the algorithm but the opposite, however this can be explained by the large amount of RAM of the computer, if it was a worse computer or larger dataset probably this change would have done a positive effect in the overall performance.
This class can process both *csv* and *tsv.gz* files.

### Tokenizer

In order to improve stemmer performance, every token that goes though the stemmer is saved in a dictionary for faster look up in later transformations.

### Indexer

This is an superclass of indexers, a SPIMI was used because it was required by the assignment but a BSBI (Block sort-based Indexing) could have been used as well.

#### SPIMI (Single Pass In Memory Indexing)

The SPIMI is characterized by not sorting during indexing but instead accumulate the postings and when some threshold is met signaling it is time to sort the terms and write the blocks to disk.
In the SPIMI constructor, in order to know which type of posting list to use, the class takes advantage of the `` PostingListFactory()`` function which uses the *factory pattern* to facilitate the construction of this class.
The ``construct_index()`` is the most complex method, this creates the final index which are all the merged blocks that will be written in disk. In order to facilitate the job for developers the ``min_k_merge_generator()`` method was implemented, this method returns a generator that abstracts all the accessed files by returning the least valuable term of all the blocks and the already merged posting list, this method proved very efficient at abstracting this complex step.
Inside the lastly mentioned method, we can find the list of generators for each file, these generators provide a buffer of lines based on the *maximum block size* and the *number of temporary blocks*.
The least valuable term of each block is added in a *priority queue* and if there is more than one with the same lower value, then those posting lists are merged and yielded. After that we just have to repopulate both the lines buffer and heap, and then it can restart the process until there is no more lines in every generator.

### Inverted Index

The inverted index is characterized by having a dictionary in which the key is the term and the value is a postings list, because of this, an abstraction was created that improves the capabilities of PostingList creation by simplifying its integration.
Multiple Posting List types are available out of the box such as **Boolean**, **Frequency** and **Positional** Posting List. These classes make it easy for anyone to use any kind of different index types and to be able to test new ideas. To create a new Posting List, all it is needed is to extend the PostingList class in the ``src/models/posting_list.py`` file, then the following methods must be implemented:
```
def __init__(self)->None:
    super().__init__(PostingType)

def add(self, doc_id:int, position:int)->None:

def get_documents(self)->List[int]:

@staticmethod
def load(line:str)->PostingList:

@staticmethod
def merge(posting_lists:List[PostingList])->PostingList:
```
After that, add the created class to the ``posting_list_types`` dictionary as seen bellow:
```python
posting_list_types = {
    PostingType.BOOLEAN: BooleanPostingList,
    PostingType.FREQUENCY: FrequencyPostingList,
    PostingType.POSITIONAL: PositionalPostingList
}
```
To use the newly created PostingList in the indexer, in this case SPIMI, add the posting type in the instantiation.
```
indexer = Spimi(max_ram_usage=95, max_block_size=50000, auxiliary_dir=BLOCK_DIR, posting_type=PostingType.POSITIONAL)
```
After only this simple steps, we have a functional index with a completly different PostingList implementation.

A ``light_search()`` method was also implemented to add searchable capabilities, it is an algorithm that if the searched term is not already inside the Inverted Index, then an access to the main index file is performed, the search in this file is done by RAF (Random Access File) in order to do a binary search since the terms are already sorted, this results in $ O(log_{2}{n}) $ complexity. In order to make the RAF work, the ``seek()`` was used to point to a particular byte, then as we can not be assured that we are not reading already in the middle of the line, we read the next line to get a clean line that will be read after. This is fine because the first line would be tested at the beginning of the algorithm to ensure it is not the searched term.

## Results

All the results were computed with a MacBookPro M1 and with the following constant inputs:

| Variable                | Value               |
| :---------------------- | ------------------- |
| stop words              | stop_words.txt      |
| min token               | 4                   |
| language                | english             |
| max block size          | 50 000              |
| max ram                 | 95                  |


### Boolean Posting List

Set of document ids.

| Dataset                                               | Original File Size | Index File Size | Index Build Time |
| :---------------------------------------------------- | ------------------ | --------------- | ---------------- |
| amazon_reviews_us_Digital_Video_Games_v1_00.tsv.gz    | 26.2 MB            | 25.8 MB         | 13.598 seconds   |
| amazon_reviews_us_Digital_Music_Purchase_v1_00.tsv.gz | 241.8 MB           | 252.5 MB        | 120.805 seconds  |
| amazon_reviews_us_Music_v1_00.tsv.gz                  | 1.4GB              | 1.75 GB         | 1096.75 seconds  |
| amazon_reviews_us_Books_v1_00.tsv.gz                  | 2.6 GB             | 2.84 GB         | 2161.79 seconds  |


### Frequency Posting List

Data structure where the document id connects to an integer that represents the number of times that term has occured inside the given document.

| Dataset                                               | Original File Size | Index File Size | Index Build Time |
| :---------------------------------------------------- | ------------------ | --------------- | ---------------- |
| amazon_reviews_us_Digital_Video_Games_v1_00.tsv.gz    | 26.2 MB            | 32,7 MB         | 14.647 seconds   |
| amazon_reviews_us_Digital_Music_Purchase_v1_00.tsv.gz | 241.8 MB           | 318,8 MB        | 2.020 minutes    |
| amazon_reviews_us_Music_v1_00.tsv.gz                  | 1.4 GB             | 2,18 GB         | 13.742 minutes   |
| amazon_reviews_us_Books_v1_00.tsv.gz                  | 2.6 GB             | 2.84 GB         | 24.310 minutes   |


### Positional Posting List

Data Structure where the document id links to a list of positions where the term has occured inside the document.


### Light Search
