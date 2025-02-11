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
    
    def add_row(self, section: str, row: dict) -> None:
        if section not in self.data:
            self.data[section] = []
        self.data[section].append(row)
        self.save()

    def add_rows(self, section: str, rows: list[dict]) -> None:
        for row in rows:
            self.add_row(section, row)

    def add(self, key, value) -> None:
        self.data[key] = value
        self.save()

    def get(self, key):
        if key in self.data:
            return self.data[key]
        return None
    
    def clear_section(self, section: str) -> None:
        self._data[section] = {}
        self.save()

    def clear(self) -> None:
        self._data = {}
        self.save()