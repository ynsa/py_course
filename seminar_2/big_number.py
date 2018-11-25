import logging

import sys

import datetime


def index(num_str, search_nums, k=5):
    arr = []
    data = search_nums if type(search_nums) == tuple else (search_nums, )
    for n in data:
        index = num_str.find(str(n))
        while index >= 0:
            arr.append(index + 1)
            index = num_str.find(str(n), index + 1)
    if len(arr) > k:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.info('The amount of entries is more then function returns.')
    return len(arr), sorted(arr)[:k]


if __name__ == '__main__':
    print(index('1212122222 ', (1, 2, 12), k=3))
    print(index('1212122222 ', 1, k=3))
