from math import floor


def distribute(arr, k):
    min_value = min(arr)
    max_value = max(arr)
    k_size = (max_value - min_value) / k
    hist = [0] * k
    for i in arr:
        interval_num = floor((i - min_value) / k_size) - (i == max_value)
        hist[interval_num] += 1
    return hist


if __name__ == '__main__':
    print(distribute([1.25, 1, 2, 1.75], 2))