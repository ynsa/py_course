import collections
from itertools import chain


# 1
def smart_function():
    """Returns amount of times that it has been called"""
    if not hasattr(smart_function, 'calls'):
        smart_function.calls = 0
    smart_function.calls += 1
    return smart_function.calls


# 4
def flatten(inter):
    result_list = []
    for i in inter:
        if i and type(i) is not str and isinstance(i, collections.Iterable):
            result_list = chain(result_list, flatten(i))
        elif i != [] and i is not None:
            result_list = chain(result_list, (i,))
    return result_list


if __name__ == '__main__':
    for i in range(5):
        assert smart_function() == i + 1

    expected = [1, 2, 0, 1, 1, 2, 1, 'ab']
    actual = flatten(
        [1, 2, range(2), [[], [1], [[2]]], (x for x in [1]), 'ab'])
    assert expected == list(actual)



