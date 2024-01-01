import fsspec
from tomlkit import dumps, parse


class Remote:
    def __init__(self, path):
        self.path = path
