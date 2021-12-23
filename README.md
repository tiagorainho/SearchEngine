# Search Engine

## Index
- [Motivation](#motivation)
- [Project Organization](#project-organization)
- [Install Dependencies](#install-dependencies)
- [How to Use](#how-to-use)
- [Tecnical Content](#content)
- [Results](#results)


## Install Dependencies

Download the code via *https*:
```bash
git clone https://github.com/tiagorainho/SearchEngine.git
```
or *ssh*:
```bash
git clone git@github.com:tiagorainho/SearchEngine.git
```
or *zip*:
```
https://github.com/tiagorainho/SearchEngine/archive/refs/heads/main.zip
```

Create virtual environment and activate it
```bash
python3 -m venv venv
source venv/bin/activate
```
Install dependencies
```bash
pip install -r requirements.txt
```

## How to use

If the file to use is not .gz, then convert it
```bash
gzip file.csv
```

Create the index
```bash
python3 src/indexer.py --stop-words stop_words.txt --min-token-length 3 --language english --max-block-size 50000 --max-ram 95 --documents datasets/example.gz --posting-list-type frequency --ranker TF_IDF --schema lnc.ltc
```
Search in the index interactively
```bash
python3 src/searcher.py --search-index cache/index/result.index --n 10
```
or search with only one query
```bash
python3 src/searcher.py --search-index cache/index/result.index --n 10 --query could you recommend me your favorite game
```

## Content

The following classes, their hierarchical structure and relevant features are the following:
- [Parser](#parser)
- [Tokenizer Index](#tokenizer)
- [Indexer](#indexer)
    - [SPIMI (Single Pass In Memory Indexing)](#spimi-single-pass-in-memory-indexing)
        - [RAM Access Improvements](#ram-access-improvements)
        - [Final Index Construction](#final-index-construction)
- [Inverted Index](#inverted-index)
    - [Posting List](#posting-list)
        - [Boolean Posting List](#boolean-posting-list)
        - [Frequency Posting List](#frequency-posting-list)
        - [Positional Posting List](#positional-posting-list)
- [Ranker](#ranker)
    - [TF-IDF](#tf-idf-ranker)
    - [BM25](#bm25-ranker)


### Parser

In order to decrease cache misses in a large list and also to better management of RAM (Random Access Memory), the ``parse()`` function does not return a list of parsed texts, instead it yields the parsed text in chuncks. This did **not** improve the performance of the algorithm but the opposite, however this can be explained by the large amount of RAM of the computer, if it was a worse computer or larger dataset probably this change would have done a positive effect in the overall performance.
This class processes *tsv.gz* files.

### Tokenizer

Is responsible to convert a text to a list of tokens, these tokens are also:
- removed based on the token length
- removed based on the stop words file
- edited by the stemmer which tries to reduce the words to more common ones

In order to improve stemmer performance, every token that goes though the stemmer is saved in a dictionary for faster look up in later transformations.

### Indexer

This is an superclass of indexers, a SPIMI was used because it was required by the assignment but a BSBI (Block Sort-Based Indexing) could have been used as well.

#### SPIMI (Single Pass In Memory Indexing)

The SPIMI is characterized by not sorting during indexing but instead accumulate the postings and when some threshold is met signaling it is time to sort the terms and write the blocks to disk.
In the SPIMI constructor, in order to know which type of posting list to use, the class takes advantage of the `` PostingListFactory()`` function which uses the *factory pattern* to facilitate the construction of this class.

##### RAM Access Improvements

When the ``add_document()`` method is being run, there is a need to calculate the RAM of the computer to ensure it does not pass the threshold given by the user. This could be done sequentialy in the code like: ``psutil.virtual_memory().percent >= self.MAX_RAM_USAGE`` however this will block the pipeline with useless calls. The better approach is to create a thread that is constantly updating a variable that contains the ram usage by the computer and then in the code we just have to compare that variable to the ``self.MAX_RAM_USAGE``. This is much better because we don't need to wait for the ``virtual_memory()`` to finish because the thread is already computing this result paralelly. The previously mentioned can be obtained by controlling the thread with events, this is also beneficial so there is not a wasteful usage of cpu while doing computations other than the ``add_document()`` method. In the end we end up with the same amount of precision as before but with much fewer interlap between the indexing process and the funcion maintaing the cap on the RAM only sacrificing a small percentage of time by managing this process compared to not doing the RAM cap, but much faster than the first mentioned way.

##### Final Index Construction

The ``construct_index()`` is the most complex method, this creates the final index which are all the merged blocks that will be written in disk. In order to facilitate the job for developers the ``min_k_merge_generator()`` method was implemented, this method returns a generator that abstracts all the accessed files by returning the least valuable term of all the blocks and the already merged posting list, this method proved very efficient at abstracting this complex step.
Inside the lastly mentioned method, we can find the list of generators for each file, these generators provide a buffer of lines based on the *maximum block size* and the *number of temporary blocks*.
The least valuable term of each block is added in a *priority queue* and if there is more than one with the same lower value, then those posting lists are merged and yielded. After that we just have to repopulate both the lines buffer and heap. Then it can restart the process until there is no more lines in every generator.

### Inverted Index

The inverted index is characterized by having a dictionary in which the key is the term and the value is a postings list, because of this, an abstraction was created that improves the capabilities of PostingList creation by simplifying its integration.

#### Posting List
Multiple Posting List types are available out of the box such as **Boolean**, **Frequency** and **Positional** Posting List. These classes make it easy for anyone to use any kind of different index types and to be able to test new ideas. To create a new Posting List, all it is needed is to extend the PostingList class in the ``src/models/posting_list.py`` file, then the following methods must be implemented:
```python
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
posting_list_types:Dict[PostingType, PostingList] = {
    PostingType.BOOLEAN: BooleanPostingList,
    PostingType.FREQUENCY: FrequencyPostingList,
    PostingType.POSITIONAL: PositionalPostingList
}
```
To use the newly created PostingList in the indexer, in this case SPIMI, add the posting type in the instantiation.
```python
indexer = Spimi(posting_type=PostingType.POSITIONAL)
```
After only this simple steps, we have a functional index with a completly different PostingList implementation.

### Ranker

A ``light_search()`` method was also implemented in the ``InvertedIndex`` to add searchable capabilities, it is an algorithm that if the searched term is not already inside the Inverted Index, then an access to the main index file is performed, the search in this file is done by RAF (Random Access File) in order to do a binary search since the terms are already sorted, this results in $ O(log_{2}{n}) $ complexity. In order to make the RAF work, the ``seek()`` method was used to point to a particular byte, then as we can not be assured that we are not reading already in the middle of the line, we read the next line to get a clean line that will be read after. This is fine because the first line would be tested at the beginning of the algorithm to ensure it is not the searched term.

The previous method cared of proper ranking because would only provide us with the documents in which a term was found. This is not that useful because we would either get a lot of documents or probably none (feast of famine). For that reason, ``rankers`` are used to provide methods that improve the efficiency of returned documents.

The default available rankers are ``TF-IDF`` and ``BM25`` and more can be created similary to the ``Posting Lists``. Extend the ``Ranker`` class found in ``src/models/ranker.py`` file and override the needed methods:
```python
    def __init__(self, posting_type: PostingType, *args, **kwargs):

    def order(self, term_to_posting_list: Dict[str, PostingList]) -> List[Tuple[int, float]]:

    def load_metadata(self, metadata: Dict[str, object]):
    
    def load_posting_list(self, posting_list_class: PostingList.__class__, line: str) -> PostingList:

    def load_tiny(line: str):

    def metadata(self) -> Dict[str, object]:

    def pos_processing(self) -> Dict[str, object]:

    def before_add_tokens(self, term_to_postinglist: Dict[str, PostingList], tokens: List[str], doc_id: int):

    def after_add_tokens(self, term_to_postinglist: Dict[str, PostingList], tokens: List[str], doc_id: int):

    def document_repr(self, posting_list: PostingList):
    
    def term_repr(self, posting_list: PostingList):
    
    def tiny_repr(self, posting_list: PostingList):

    def merge_calculations(self, posting_list: PostingList):
```

Then add the new class to the Factory method like the previous:
```python
ranking_methods:Dict[RankingMethod, Ranker] = {
    RankingMethod.TF_IDF: TF_IDF_Ranker,
    RankingMethod.BM25: BM25_Ranker
}
```

To use the newly created Ranker in the indexer, in this case SPIMI, add the ranker in the constructor.
```python
ranker = RankerFactory(RankingMethod.BM25)
indexer = Spimi(posting_type=PostingType.Frequency, ranker=ranker)
```

An example for versatility was implemented in the ``TF-IDF ranker``, where we can provide schemas to use inside the class. 3 functions where implemented to calculate the scores of documents but each function was used twice. 2 of the previous 3 functions use other 3 functions and the other uses 2, therefore, $ 3\times{3\times{2}} = 18 $ combinations are possible.

## Results

The arguments provided for the **index creation** are the following:

| Variable               | Value             |
| :--------------------- | ----------------- |
| stop words             | stop_words.txt    |
| min token              | 3                 |
| language               | english           |
| max block size         | 50 000            |
| max ram                | 95                |


All results were performed using a MacBookPro M1 with the following specs:
- Apple Air M1
- 8 GB Ram
- 512 GB SSD

The values were calculated on the first delivery, now the speeds are even lower when doing the same thing. The time will also greatly depend on the ranker implementation.

### Boolean Posting List

Set of document ids.

| Dataset                  | Original File Size | Index File Size | Index Build Time | Temporary Blocks | Nº of Terms | 
| :----------------------- | ------------------ | --------------- | ---------------- | ---------------- | ----------- |
| Digital_Video_Games      | 26.2 MB            | 25.80 MB        | 13.598 sec       | 2                | 53 594      |
| Digital_Music_Purchase   | 241.8 MB           | 252.50 MB       | 1.894 min        | 20               | 312 903     |
| Music                    | 1.4 GB             | 1.75 GB         | 12.982 min       | 164              | 1 041 499   |
| Books                    | 2.6 GB             | 2.84 GB         | 22.241 min       | 239              | 1 626 371   |


### Frequency Posting List

Data structure where the document id connects to an integer that represents the number of times that term has occured inside the given document.

| Dataset                  | Original File Size | Index File Size | Index Build Time | Temporary Blocks | Nº of Terms | 
| :----------------------- | ------------------ | --------------- | ---------------- | ---------------- | ----------- |
| Digital_Video_Games      | 26.2 MB            | 32.70 MB        | 14.647 sec       | 2                | 53 594      |
| Digital_Music_Purchase   | 241.8 MB           | 318.80 MB       | 2.020 min        | 20               | 312 903     |
| Music                    | 1.4 GB             | 2.18 GB         | 13.742 min       | 164              | 1 041 499   |
| Books                    | 2.6 GB             | 3.54 GB         | 24.310 min       | 239              | 1 626 371   |


### Positional Posting List

Data Structure where the document id links to a list of positions where the term has occured inside the document.

| Dataset                  | Original File Size | Index File Size | Index Build Time | Temporary Blocks | Nº of Terms |
| :----------------------- | ------------------ | --------------- | ---------------- | ---------------- | ----------- |
| Digital_Video_Games      | 26.2 MB            | 40.03 MB        | 20.878 sec       | 2                | 53 594      |
| Digital_Music_Purchase   | 241.8 MB           | 370.00 MB       | 3.432 min        | 20               | 312 903     |
| Music                    | 1.4 GB             | 2.64 GB         | 26.953 min       | 164              | 1 041 499   |
| Books                    | 2.6 GB             | 4.33 GB         | 46.614 min       | 239              | 1 626 371   |


### Search

The following table presents the statistics and search results related to the search of the query list provided by the professor and using an index with ``frequency posting lists`` with both ``BM25`` and ``TF-IDF`` rankers.

The search result files are in inside the ``results``folder.

#### TF-IDF Ranker

| Dataset                  | Index build time | Avg Searcher Startup Time | Avg Search Time | Files                    |
| :----------------------- | ---------------- | ------------------------- | ----------- | ------------------------ |
| Digital_Music_Purchase   | 181.83 sec       | 0.0045 ms                 | 0.130 ms    | tf_idf_digital_music.txt |
| Music                    | 1.6 sec       | 0.0044 ms             | 0.745 ms    | tf_idf_music.txt         |

#### BM25 Ranker

| Dataset                  | Index build time | Avg Searcher Startup Time | Avg Search Time | Files                  |
| :----------------------- | ---------------- | --------------------- | ----------- | ---------------------- |
| Digital_Music_Purchase   | 120.21 sec       | 0.0045 ms             | 0.130 ms    | bm25_digital_music.txt |
| Music                    | 120.6 sec       | 0.0044 ms             | 0.745 ms    | bm25_music.txt         |

