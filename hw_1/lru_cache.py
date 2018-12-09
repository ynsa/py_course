import time
from collections import deque
from random import randint
from threading import Timer
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

    def __eq__(self, other):
        return self.key == other


class LRUCache:
    def __init__(self, size: int = 2, default_ttl: int = 60):
        assert default_ttl > 0, "`default_ttl` should be positive."

        self._default_ttl = default_ttl
        self._storage = deque(maxlen=size)
        self._ttl = dict()

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

    def _pop_invalid(self, ttl_time):
        invalid_list = self._ttl.get(ttl_time, [])
        for key in invalid_list:
            print(key)
            try:
                self._storage.remove(key)
            except ValueError:
                pass
        try:
            self._ttl.pop(ttl_time)
        except KeyError:
            pass

    def index(self, key):
        """If record exists returns index else returns -1 """
        try:
            return self._storage.index(key)
        except ValueError:
            return -1

    def get(self, key):
        index = self.index(key)
        if index != -1:
            record = self._storage[index]
            self._storage.remove(key)
            self._storage.append(record)
            return record.value
        return None

    def pop(self, key):
        index = self.index(key)
        if index != -1:
            key_time = self._storage[index].ttl
            ttl_list = self._ttl[key_time]
            try:
                ttl_list.pop(ttl_list.index(key))
                if not ttl_list:
                    self._ttl.pop(key_time)
                    print(f'pop {key}')
                    self._storage.remove(index)
            except ValueError:
                pass

    def clean(self):
        self._storage.clear()

    def push(self, key, value, ttl: int = None):
        if not ttl:
            ttl = self.default_ttl
        ttl_time = int(time.time() + ttl)
        ttl_list = self._ttl.get(ttl_time, None)
        if not ttl_list:
            self._ttl[ttl_time] = [key, ]
            Timer(ttl, self._pop_invalid, [ttl_time, ]).start()
        else:
            ttl_list.append(key)
        if self.size == self.max_size:
            self.pop(self._storage[0].key)

        self._storage.append(Record(key, value, int(time.time() + ttl)))


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
