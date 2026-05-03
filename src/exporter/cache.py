# src/exporter/cache.py
import json
import os

class IMDbCache:
    def __init__(self, filename):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)

    def get(self, show_id):
        return self.data.get(str(show_id))

    def set(self, show_id, imdb_id):
        self.data[str(show_id)] = imdb_id
        self.save()
