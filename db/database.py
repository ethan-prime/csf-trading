import json
import os
from collections import UserDict

class Database:
    def __init__(self, db_file: str) -> None:
        self.file = db_file
        self._data = None

    def read_data(self) -> None:
        if not os.path.exists(self.file):
            with open(self.file, 'w', encoding='utf-8') as f:
                f.write("{}")
        with open(self.file, 'r', encoding='utf-8') as f:
            self._data = json.loads(f.read())

    def save(self) -> None:
        if self._data is None:
            raise Exception("attempted to write data NONE")
        with open(self.file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self._data))

    @property
    def data(self) -> dict:
        if self._data is None:
            self.read_data()
        return self._data