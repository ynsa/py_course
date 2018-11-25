import math


def get_true_morse_k(k, values):
    if not k:
        return 0
    if k % 2 == 0:
        return values[math.floor(k / 2)]
    else:
        return 1 - values[math.floor(k / 2)]


def get_nearest_power(number):
    power = 1
    while power < number:
        power += 8
    return power - 2 if power > 2 else 1


def get_true_morse_k_bin(k, value):
    if not k:
        return value
    else:
        value = get_true_morse_k_bin(k - 1, value)
        new_value = (~value & get_nearest_power(value))
        move = pow(2, k - 1)
        res = value + (new_value << move)
        return res


def get_sequence_item(n):
    values = []
    for i in range(0, pow(2, n)):
        values.append(get_true_morse_k(i, values))
    str_bytes = ''.join(str(val) for val in values)
    return int(str_bytes[::-1], base=2)


if __name__ == '__main__':
    print(int(get_true_morse_k_bin(3, 0)))
    print(get_sequence_item(3))
