from pathlib import Path
from typing import Dict, Set
from nltk.stem.snowball import SnowballStemmer
from string import punctuation
import re


class Tokenizer:
    min_token_length: int or None
    snow_stemmer: SnowballStemmer or None
    stop_words: Set[str] or None
    transforms: Dict[str, str]


    def __init__(self,
                 min_token_length: int = None,
                 stop_words_path: str = None,
                 stem_lang: str = None) -> None:
        """
        __init__ creates a new instance of Tokenizer

        :param min_token_length: min length of accepted tokens
        :param stop_words_path: path to the file of stop words
        :param stem_lang: language of the tokens
        :return: None
        """
        self.transforms = dict()
        self.min_token_length = min_token_length
        self.snow_stemmer = SnowballStemmer(
            language=stem_lang) if stem_lang != None else None

        if stop_words_path != None:
            with open(Path(stop_words_path)) as file:
                self.stop_words = {w for w in file.read().split("\n")}
        else:
            self.stop_words = None


    def tokenize(self, text: str):
        """
        tokenize reads a text and tokenizes it using provided settings 

        :param text: variable length text to tokenize
        :return: None
        """

        no_ponctuation = filter(lambda w: w not in punctuation, text)
        lowered = "".join(no_ponctuation).lower()
        tokens = list(re.split(' |,|\t|\n',lowered))

        if self.min_token_length != None:
            tokens = filter(lambda n: len(n) >= self.min_token_length, tokens)

        if self.stop_words != None:
            tokens = filter(lambda n: n not in self.stop_words, tokens)

        if self.snow_stemmer != None:
            aux = []
            for token in tokens:
                transform = self.transforms.get(token)
                if transform == None:
                    transform = self.snow_stemmer.stem(token)
                    self.transforms[token] = transform
                aux.append(transform)
            tokens = aux

        return list(tokens)
