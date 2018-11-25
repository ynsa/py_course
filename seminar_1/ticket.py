def check_luck(ticket):
    digits = [int(i) for i in str(ticket)]
    return sum(digits[:3]) == sum(digits[3:])


def get_nearest_lucky_ticket(ticket):
    if check_luck(ticket):
        return ticket
    i = 1
    while True:
        if ticket + i < pow(10, 6) and check_luck(ticket + i):
            return ticket + i
        elif ticket - i >= pow(10, 5) and check_luck(ticket - i):
            return ticket - i
        else:
            i += 1
    else:
        print('Can\'t find.')


if __name__ == '__main__':
    print(get_nearest_lucky_ticket(500000))
