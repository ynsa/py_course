# 1
import operator
from functools import reduce
from itertools import filterfalse, chain


def smart_function():
    """Returns amount of times that it has been called"""
    if not hasattr(smart_function, 'calls'):
        smart_function.calls = 0
    smart_function.calls += 1
    return smart_function.calls


# def flatten(iter):
#     if hasattr(iter, '__iter__'):
#         for item in iter:
#             x = flatten(item)
#     else:
#         yield iter

def flatten(inter):
    l = []
    if hasattr(inter, '__iter__'):
        print(list(reduce(lambda a, x: chain(flatten(a), flatten(x)), inter)))
        return filterfalse(lambda x: not x, reduce(lambda a, x: chain(flatten(a), flatten(x)), inter))
        # return filterfalse(lambda x: not x, reduce(lambda a: l.append(flatten(a)), inter))
    else:
        return [inter, ]


if __name__ == '__main__':
    for i in range(5):
        assert smart_function() == i + 1

    expected = [1, 2, 0, 1, 1, 2, 1, 'ab']
    actual = flatten([1, 2, range(2), [[], [1], [[2]]], (x for x in [1]), 'ab'])
    for i in actual:
        print(i)
    # assert expected == list(actual)


