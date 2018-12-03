import contextlib
import time
import timeit
import requests


def profile(method):
    def timed(*args, **kw):
        start = timeit.default_timer()
        result = method(*args, **kw)
        print(f'{method.__name__}: {timeit.default_timer() - start:.5f}s')
        return result
    return timed


@contextlib.contextmanager
def timer():
    start = timeit.default_timer()
    try:
        yield
    finally:
        print(f'block time: {timeit.default_timer() - start:.5f}s')


class SafeRequest:
    def __init__(self, timeout: float = 3, default=None):
        self._timeout = timeout
        self._default = default

    def __call__(self, *args, **kwargs):
        kwargs['timeout'] = self._timeout
        response = requests.request(*args, **kwargs)
        if response.status_code == 404 and self._default:
            return self._default
        response.raise_for_status()
        return response


# test functions

@profile
def nyam(a=1):
    time.sleep(a)


@profile
def some_function():
        sum(range(10000))


if __name__ == '__main__':
    nyam(1)
    result = some_function()
    with timer():
        assert sum(range(10000, 20000)) == 149995000
    safe_request = SafeRequest(timeout=5, default=None)
    print(safe_request('get', 'http://yandex.ru/'))
    try:
        print(safe_request('get', 'https://yandex.by/maps/asd'))
    except requests.HTTPError as e:
        print(f'Get {e}')
    safe_request = SafeRequest(timeout=5, default="My 404 default.")
    print(safe_request('get', 'http://yandex.ru/'))
    print(safe_request('get', 'https://yandex.by/maps/asd'))
    safe_request = SafeRequest(timeout=0.05, default="My 404 default")
    try:
        print(safe_request('get', 'http://google.ru/'))
    except (requests.ConnectTimeout, requests.ReadTimeout) as e:
        print(f'Get {e}')
