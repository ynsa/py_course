# 1
def smart_function():
    """Returns amount of times that it has been called"""
    if not hasattr(smart_function, 'calls'):
        smart_function.calls = 0
    smart_function.calls += 1
    return smart_function.calls


if __name__ == '__main__':
    for i in range(5):
        assert smart_function() == i + 1



