import time
from random import randint
from typing import Union


class Record:
    def __init__(self, key: str, value=None, ttl: Union[int, float] = 60):
        self._key = key
        self._value = value
        self._ttl = ttl
        self._calls = 0

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @property
    def ttl(self):
        return self._ttl

    @property
    def calls(self):
        return self._calls

    @ttl.setter
    def ttl(self, value):
        self._ttl = value

    @calls.setter
    def calls(self, value):
        self._calls = value

    def __eq__(self, other):
        return self.key == other


class LRUCache:
    def __init__(self, size: int = 2, default_ttl: int = 60):
        assert default_ttl > 0, "`default_ttl` should be positive."
        assert size > 0, "`size` should be positive."

        self._default_ttl = default_ttl
        self._max_size = size
        self._storage = dict()
        self._ttl = dict()
        self._min_call_value = 0

    @property
    def max_size(self):
        return self._max_size

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

    def exist(self, key):
        """If record exists returns value else returns None """
        return self._storage.get(key, None) is None

    def get(self, key):
        record = self._storage.get(key, None)
        if record:
            if record.ttl >= time.time():
                self._ttl[key] += 1
                return record.value
            else:
                self._ttl.pop(key)
                self._storage.pop(key)
        return None

    def pop(self, key):
        record = self._storage.get(key, None)
        if record:
            self._ttl.pop(key)
            print(f'pop {key}')
            self._storage.pop(key)

    def clean(self):
        self._storage.clear()

    def push(self, key, value, ttl: int = None):
        assert isinstance(ttl, type(None)) or ttl > 0, \
            "`ttl` should be positive."
        if not ttl:
            ttl = self.default_ttl
        ttl_time = int(time.time() + ttl)
        self._ttl[key] = 0
        if self.size == self.max_size:
            not_popular = min(self._ttl, key=self._ttl.get)
            self._ttl.pop(not_popular)
            self.pop(not_popular)

        self._storage[key] = (Record(key, value, ttl_time))


if __name__ == '__main__':
    cache = LRUCache(size=25, default_ttl=5)
    for i in range(1, 5000000):
        if not i % 5:
            cache.get(i - 5)
            if i == 5:
                print(f'size: {cache.size}\t max: {cache.max_size}')
        if i % 10 == 0:
            cache.push(i, f'{i}-val(15)', 10)
        else:
            if i == 25:
                print('ttl: ', cache.default_ttl)
                cache.default_ttl = 10
            cache.push(i, f'{i}-val')

        cache.get(i - randint(0, i))

    print(cache.get(5))
    print(cache.get(28))
    print(cache.get(29))
