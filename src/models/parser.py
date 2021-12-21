from typing import Dict, Set
from pathlib import Path
import csv
import sys
import gzip


class Parser:
    file_path: str
    doc_id_column: str
    columns: Set[str]

    def __init__(self, file_path: str, doc_id_column: str, columns: Set[str]) -> None:
        """
        __init__ creates a new instance of Parser

        :param file_path: file to be parsed path
        :param doc_id_column: name of the docId column
        :param columns: all columns names to be parsed
        :return: None
        """
        assert Path(file_path).exists()
        assert len(doc_id_column) != 0
        assert len(columns) != 0

        self.file_path = file_path
        self.doc_id_column = doc_id_column
        self.columns = columns

        csv.field_size_limit(sys.maxsize)

    def parse(self, delimiter: str) -> Dict[int, str]:
        """
        parse parses the current file using provided columns and doc_id_column

        :param delimiter: csv delimiter char
        :return: Dictionary containing doc id as key and text as value
        """

        with gzip.open(self.file_path, "rt", encoding='utf-8') as file:
            data = csv.DictReader(file, delimiter=delimiter)

            for row in data:
                values = " ".join([row[k]
                                  for k in row.keys() if k in self.columns and row[k] != None])

                yield (row[self.doc_id_column], values)
