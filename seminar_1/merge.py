

def merge(seq_1, seq_2):
    res_type = type(seq_1)
    res_seq = []
    seq_1 = list(seq_1)
    seq_2 = list(seq_2)
    counter = len(seq_1) + len(seq_2)
    x_1 = x_2 = None
    for i in range(0, counter):
        x_1 = seq_1.pop(0) if len(seq_1) and not x_1 else x_1
        x_2 = seq_2.pop(0) if len(seq_2) and not x_2 else x_2
        if x_1 and x_2:
            if x_1 <= x_2:
                res_seq.append(x_1)
                x_1 = None
            else:
                res_seq.append(x_2)
                x_2 = None
        elif x_1:
            res_seq.append(x_1)
            res_seq.extend(seq_1)
        elif x_2:
            res_seq.append(x_2)
            res_seq.extend(seq_2)
    return res_type(res_seq)


if __name__ == '__main__':
    print(merge((1, ), (2, )))
