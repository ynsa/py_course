def fizzbuzz(min_val, max_val, conditions):
    new_arr = []
    keys = conditions.keys()
    for i in range(min_val, max_val):
        vl = ''
        flag = False
        for k in keys:
            if i % k == 0:
                vl += conditions[k]
                flag = True
        new_arr.append(vl if flag else str(i))
    print(' '.join(new_arr))


def fizzbuzz2(min_val, max_val, x1=3, x2=7, s='FizzBuzz'):
    print(' '.join([s if not i % (x1 * x2) else s[:4] if not i % x1 else s[4:] if not i % x2 else str(i) for i in range(min_val, max_val)]))


if __name__ == '__main__':
    conditions = {
        3: 'Fizz',
        7: 'Buzz',
    }
    fizzbuzz(1, 102, conditions)
    fizzbuzz2(1, 102)
