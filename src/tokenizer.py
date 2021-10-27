# porterstemming

import string
import csv
import sys
import re
from typing import Dict, List, Set
from collections import defaultdict


class Tokenizer:
    path: str
    tokens: Dict[int, Set[str]]

    def __init__(self, path: str) -> None:
        self.tokens = defaultdict(set)
        self.path = path
        csv.field_size_limit(sys.maxsize)

    def tokenize(self, docId: str, columns: List[str]):
        with open(self.path, newline='') as file:
            self.data = csv.DictReader(file, delimiter="\t")
            for row in self.data:
                doc_id = row[docId]
                text = ""

                for key in row:
                    if key not in columns:
                        continue
                    text += f"{row[key]} "

                text = text.translate(
                    (str.maketrans('', '', string.punctuation))).lower()

                for token in re.split("[ \t]", text):
                    self.tokens[doc_id].add(token)

    def get_tokens(self):
        return self.tokens
