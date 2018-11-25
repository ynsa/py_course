from itertools import product

coins = [1, 2, 5, 10]


def fill_table(n, table):
    for i, j in product(range(1, len(coins)), range(1, n + 1)):
        table[i][j] = table[i - 1][j] + (table[i][j - coins[i]]
                                         if j >= coins[i] else 0)
    return table


def exchange_money(n):
    mas = [[0] * (n + 1)] * len(coins)
    mas[0] = [1] * (n + 1)
    for j in range(0, len(coins)):
        mas[j][0] = 1
    fill_table(n, mas)
    return mas[len(coins) - 1][n]


if __name__ == '__main__':
    print(exchange_money(100))
    # print([exchange_money(i) for i in range(0, 13)])
