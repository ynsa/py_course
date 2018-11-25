import time


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000.0)
        else:
            print('%r  %2.16f ms' %
                  (method.__name__, (te - ts) * 1000.0))
        return result
    return timed