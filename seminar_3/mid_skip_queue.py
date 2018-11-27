from collections import deque
from pprint import pformat


class MidSkipQueue(object):
    def __init__(self, k, iterable=None):
        assert isinstance(k, int), (
            'The `k` argument must be an instance of '
            '`int`, not `{}.{}`.'.format(
                k.__class__.__module__, k.__class__.__name__)
        )
        assert k > 0, 'The `k` argument must be positive.'

        assert isinstance(iterable, type(None)) or \
            hasattr(iterable, '__iter__'), (
                'The `iterable` argument must implement `__iter__` method,'
                ' `{}.{}` doesn\'t do it.'.format(
                    iterable.__class__.__module__, iterable.__class__.__name__)
            )

        self._k = k
        self._head = []
        self._tail = deque(maxlen=k)
        self._list = None

        if iterable:
            self.__add__(iterable)

    @property
    def k(self):
        return self._k

    @property
    def list(self):
        if not self._list:
            self._list = self._head + list(self._tail)
        return self._list

    def copy(self):
        return self.__class__(self.k, self.list)

    def index(self, *args, **kwargs):
        try:
            return self.list.index(*args, **kwargs)
        except ValueError:
            return -1

    def append(self, p_object, *args):
        if len(self._head) < self.k:
            self._head.append(p_object)
        else:
            self._tail.append(p_object)
        if len(args):
            self.__add__(args)
        self._list = None

    def __add__(self, another):
        if len(self._head) < self.k:
            count = min(len(another), self.k - len(self._head))
            self._head += another[:count]
            another = another[count:]
        if len(another):
            count = min(self.k, len(another))
            if count == self.k:
                self._tail = deque(another[len(another) - count:],
                                   maxlen=self.k)
            else:
                self._tail.extend(another[len(another) - count:])
        self._list = None
        return self

    def __eq__(self, another):
        assert isinstance(another, MidSkipQueue), (
            'The `another` argument must be an instance of '
            '`MidSkipQueue`, not `{}.{}`.'.format(
                another.__class__.__module__, another.__class__.__name__)
        )

        if self.k == another.k:
            return self.list == another.list
        return False

    def __iter__(self):
        return iter(self.list)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, y):
        return self.list.__getitem__(y)

    def __contains__(self, *args, **kwargs):
        return self.list.__contains__(*args, **kwargs)

    def __str__(self):
        # TODO: change
        return pformat(self.list, indent=2, width=2)


class MidSkipPriorityQueue(MidSkipQueue):
    def __init__(self, k, iterable=None):
        assert isinstance(k, int), (
            'The `k` argument must be an instance of '
            '`int`, not `{}.{}`.'.format(
                k.__class__.__module__, k.__class__.__name__)
        )
        assert k > 0, 'The `k` argument must be positive.'

        assert isinstance(iterable, type(None)) or \
            hasattr(iterable, '__iter__'), (
                'The `iterable` argument must implement `__iter__` method,'
                ' `{}.{}` doesn\'t do it.'.format(
                    iterable.__class__.__module__, iterable.__class__.__name__)
            )

        self._k = k
        self._head = []
        self._tail = []
        # self._head = PriorityQueue(maxsize=k)
        # self._tail = PriorityQueue(maxsize=k)

        self._list = None

        if iterable:
            self.__add__(iterable)

    def _find_max(self, seq):
        return max(range(len(seq)), key=seq.__getitem__)

    def _find_min(self, seq):
        return min(range(len(seq)), key=seq.__getitem__)

    def _add_tail(self, item):
        if not len(self._tail):
            self._tail.append(item)
        else:
            value = item
            if item > self._tail[0]:
                value = self._tail[0]
                self._tail[0] = item
            if len(self._tail) < self.k:
                self._tail.append(value)
            else:
                j = self._find_min(self._tail)
                if item > self._tail[j]:
                    self._tail[j] = value

    def append(self, p_object, *args):
        value = p_object
        if len(self._head) < self.k:
            if len(self._head) and p_object < self._head[0]:
                value = self._head[0]
                self._head[0] = p_object
            self._head.append(value)
        else:
            i = self._find_max(self._head)
            if p_object < self._head[i]:
                if p_object < self._head[0] and i:
                    value = self._head[0]
                    self._head[0] = p_object
                self._add_tail(self._head[i])
                self._head[i] = value
            else:
                self._add_tail(p_object)
                # j = self._find_min(self._tail)
                # if len(self._tail) < self.k:
                #     if p_object > self._tail[0]:
                #         value = self._tail[0]
                #         self._tail[0] = p_object
                # if p_object > self._tail[j]:
                #     if p_object > self._tail[0]:
                #         value = self._tail[0]
                #         self._tail[0] = p_object
                #     self._tail[j] = value
        if len(args):
            self.__add__(args)
        self._list = None

    def __add__(self, another):
        for item in another:
            self.append(item)
        self._list = None
        return self


if __name__ == '__main__':
    q = MidSkipPriorityQueue(1)
    q.append(-1)  # q: [-1]
    assert q.list == [-1]
    q += (-2, -3)  # q: [-3, -1] - the smallest and the largest items
    assert q.list == [-3, -1]
    q.append(4)  # q: [-3, 4] - the largest item is replaced
    assert q.list == [-3, 4]
    q.append(-5)  # q: [-5, 4] - the smallest item is replaced
    assert q.list == [-5, 4]

    q = MidSkipPriorityQueue(2)
    assert q.list == []
    q += (6, 5, 3, 1, 2, 4, 8, 7)
    assert q.list == [1, 2, 8, 7]
    # q = PriorityQueue(maxsize=3)
    # q.put(5)
    # q.put(1)
    # q.put(2)
    # q.put(6)
    # pprint(q.queue)
    # q = MidSkipQueue(2, (1, 2, 3, 4, 5))
    q = MidSkipQueue(1)
    q2 = q.copy()
    q.append(-1)
    q += (-2, -3)
    assert q.list == [-1, -3]
    assert q2.list == []
    assert q2.k == 1
    q.append(4)
    assert q.list == [-1, 4]
    q.append(5)
    assert q.list == [-1, 5]
    assert q[1] == 5
    assert q.index(5) == 1
    assert q.index(55) == -1

    q = MidSkipQueue(2, "Hello!")
    assert q.list == ['H', 'e', 'o', '!']
    # print(q)
    # q += [x for x in range(1001, 9000)]
    # print(q)
    # q.append(1501, 1502, "1503", "1504")
    # print(q)
