from pathlib import Path
from typing import List
from nltk.stem.snowball import SnowballStemmer
from string import punctuation


class Tokenizer:
    min_token_length: int or None
    snow_stemmer: SnowballStemmer or None
    stop_words: List[str] or None

    def __init__(self,
                 min_token_length: int = None,
                 stop_words_path: str = None,
                 stem_lang: str = None) -> None:

        self.min_token_length = min_token_length
        self.snow_stemmer = SnowballStemmer(
            language=stem_lang) if stem_lang != None else None

        if stop_words_path != None:
            with open(Path(stop_words_path)) as file:
                self.stop_words = [w for w in file.read().split("\n")]
        else:
            self.stop_words = None

    def tokenize(self, text: str):
        no_ponctuation = filter(lambda w: w not in punctuation, text)
        lowered = "".join(no_ponctuation).lower()
        tokens = set(lowered.split(" "))

        if self.min_token_length != None:
            tokens = filter(lambda n: len(n) >= self.min_token_length, tokens)

        if self.stop_words != None:
            tokens = filter(lambda n: n not in self.stop_words, tokens)

        if self.snow_stemmer != None:
            tokens = map(lambda n: self.snow_stemmer.stem(n), tokens)

        return list(tokens)
