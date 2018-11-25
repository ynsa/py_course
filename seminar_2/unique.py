from collections import Counter


def compress(array):
    return list(Counter(array).items())


if __name__ == '__main__':
    print(compress([1, 2, 1, 1]))
