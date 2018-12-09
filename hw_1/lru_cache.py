import heapq
import time
from collections import deque
from threading import Event
from typing import Union


class Record:
    def __init__(self, key: str, value=None, ttl: Union[int, float] = 60):
        self._key = key
        self._value = value
        self._ttl = ttl

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        self._ttl = value

    def __lt__(self, other):
        return self.ttl > other.ttl

    def __eq__(self, other):
        return self.key == other.key


class LRUCache:
    def __init__(self, size: int = 2, default_ttl: int = 60):
        self._default_ttl = default_ttl
        self._storage = deque(maxlen=size)
        self._event = Event()

    @property
    def max_size(self):
        return self._storage.maxlen

    @property
    def default_ttl(self):
        return self._default_ttl

    @default_ttl.setter
    def default_ttl(self, value: int):
        assert value > 0, "`value` should be positive."
        self._default_ttl = value

    @property
    def size(self):
        return len(self._storage)

    def index(self, key):
        """If record exists returns index else returns -1 """
        return self._storage.index(key)

    def get(self, key):
        index = self.index(key)
        if index != -1:
            # record = self._storage.pop(index)
            record = self._storage[index]
            record.ttl += self.default_ttl
            return record.value
        return None

    def pop(self, key):
        index = self.index(key)
        if index != -1:
            self._storage.pop(index)

    def clean(self):
        self._storage.clear()

    def push(self, key, value, ttl: int = None):
        self._storage.append(Record(key, value, ttl=(time.time() + ttl)))



if __name__ == '__main__':
    pass