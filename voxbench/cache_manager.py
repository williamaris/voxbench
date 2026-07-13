import os
import json
import hashlib
from pathlib import Path

CACHE_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
        '.cache.json'
    )
)

class CacheManager:
    def __init__(self):
        try:
            with open(CACHE_FILE, "r") as f:
                self.cache = json.load(f)

        except (json.JSONDecodeError, FileNotFoundError):
            self.cache = {}

    def hash_path(self, path):
        h = hashlib.sha256()

        for p in sorted(Path(path).rglob("*")):
            rel_p = p.relative_to(path)

            if p.is_dir():
                h.update(f"dir:{rel_p}".encode())

            elif p.is_file():
                h.update(f"file:{rel_p}".encode())

                with open(p, "rb") as f:
                    while chunk := f.read(8192):
                        h.update(chunk)

        digest = h.hexdigest()

        return digest

    def set_hash(self, key, hash):
        self.cache[key] = hash
        self._save()

    def get_hash(self, key):
        return self.cache.get(key)

    def _save(self):
        with open(CACHE_FILE, "w", encoding = "utf-8") as f:
            json.dump(self.cache, f, indent=4)

cache_manager = CacheManager()

def get_cache_manager():
    return cache_manager