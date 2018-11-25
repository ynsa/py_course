from math import sqrt, ceil, factorial


def get_primes(n):
    # return [i for i in range(1, n + 1) if not any([i % j == 0 for j in range(2, ceil(sqrt(i) + 1))])]
    return [i for i in range(2, n + 1) if not((factorial(i - 1) + 1) % i)]


if __name__ == '__main__':
    print(get_primes(12))