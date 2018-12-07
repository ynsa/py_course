import operator
from itertools import starmap


def transpose(iter):
    pass


# 3
def scalar_product(iter_1, iter_2):
    try:
        u = zip(map(float, iter_1), map(float, iter_2))
        return sum(starmap(operator.mul, u))
    except ValueError:
        return None


if __name__ == '__main__':
    print(scalar_product([1, 2], [-1, 1]))
    expected = 1
    actual = scalar_product([1, '2'], [-1, 1])
    assert expected == actual
    actual = scalar_product([1, 'abc'], [-1, 1])
    assert actual is None
