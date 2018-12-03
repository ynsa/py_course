import contextlib
import logging
from time import sleep
from typing import Union, Type, List

# ---------------------------------
# logging

logger = logging.getLogger()
logger.level = logging.ERROR

# END logging
# ---------------------------------


def _error_handler(e, re_raise: bool = True, log_traceback: bool = True,
                   exc_type:
                   Union[Type[Exception], List[Type[Exception]]] = Exception):
    """Help function for both context manager and decorator"""
    if type(e) in exc_type if type(exc_type) == list else type(
            e) == exc_type:
        if not re_raise:
            return
    logger.exception(e, exc_info=log_traceback)


@contextlib.contextmanager
def handle_error_context(*args, **kwargs):
    try:
        yield
    except Exception as e:
        _error_handler(e, *args, **kwargs)


def handle_error(tries: int = 1, delay: float = 0, backoff: float = 1, **kwargs):
    assert isinstance(tries, type(None)) or tries > 0, (
            'The `tries` argument must be positive int or None'.format(
                tries.__class__.__module__, tries.__class__.__name__)
        )

    assert delay > 0, 'The `delay` argument must be positive.'

    assert backoff > 0, 'The `backoff` argument must be positive.'

    def _inner(method):
        def __inner(*args, **kw):
            _delay = delay
            _tries = tries if type(tries) == int else True
            while _tries:
                try:
                    return method(*args, **kw)
                except Exception as e:
                    if type(tries) == int:
                        _tries -= 1
                        if not _tries:
                            _error_handler(e, **kwargs)
                        else:
                            sleep(_delay)
                            _delay *= backoff
        return __inner
    return _inner


# test functions

@handle_error(tries=3, delay=2, backoff=0.5)
def nyam():
    l = [0]
    l[2] = 8


@handle_error(tries=3, delay=2, backoff=0.5, re_raise=False, exc_type=IndexError)
def nyam1():
    l = [0]
    l[2] = 8


@handle_error(tries=3, delay=2, backoff=0.5, re_raise=True, exc_type=IndexError)
def nyam2():
    l = [0]
    l[2] = 8


@handle_error(tries=2, delay=2, backoff=0.5, re_raise=False,
              exc_type=ValueError, log_traceback=False)
def nyam3():
    l = [0]
    l[2] = 8


if __name__ == '__main__':
    with handle_error_context(re_raise=False, exc_type=ValueError):
        raise ValueError()

    with handle_error_context(re_raise=True, log_traceback=False):
        l = [0]
        l[2] = 8

    with handle_error_context(
            re_raise=False, exc_type=(ValueError, ArithmeticError)):
        l = [0]
        l[int(2/0)] = 8

    with handle_error_context(
            re_raise=False,
            exc_type=(ValueError, ArithmeticError, ZeroDivisionError)):
        l = [0]
        l[int(2/0)] = 8

    with handle_error_context(re_raise=False, exc_type=ValueError):
        raise ValueError()

    with handle_error_context(re_raise=False):
        raise Exception()

    with handle_error_context(re_raise=False, exc_type=ValueError, log_traceback=False):
        l = [0]
        l[2] = 8

    nyam()
    nyam1()
    nyam2()
    nyam3()
