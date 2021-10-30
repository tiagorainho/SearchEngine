from typing import Set
from pathlib import Path
import csv
import sys


class Parser:
    file_path: str
    doc_id_column: str
    columns: Set[str]

    """
    __init__ creates a new instance of Parser

    :param file_path: file to be parsed path
    :param doc_id_column: name of the docId column
    :param columns: all columns names to be parsed
    :return: None
    """

    def __init__(self, file_path: str, doc_id_column: str, columns: Set[str]) -> None:
        assert Path(file_path).exists()
        assert len(doc_id_column) != 0
        assert len(columns) != 0

        self.file_path = file_path
        self.doc_id_column = doc_id_column
        self.columns = columns

        csv.field_size_limit(sys.maxsize)

    """
    parse parses the current file using provided columns and doc_id_column

    :param delimiter: csv delimiter char
    :return: Parsed text
    """

    def parse(self, delimiter: str) -> str:
        text = ""

        with open(self.file_path) as file:
            data = csv.DictReader(file, delimiter=delimiter)

            for row in data:
                values = [row[k] for k in row.keys(
                ) if k in self.columns or k == self.doc_id_column]
                text += ",".join(values)

        return text
