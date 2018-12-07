# 5
class BoundedMeta(type):
    limits = dict()
    amounts = dict()

    def __new__(mcs, name, bases, namespace, **kwargs):
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, attrs, max_instance_count=1, **kwargs):
        cls.limits[name] = max_instance_count
        cls.amounts[name] = 0
        super().__init__(name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        if isinstance(cls.limits[cls.__name__], type(None)) or \
                cls.amounts[cls.__name__] < cls.limits[cls.__name__]:
            cls.amounts[cls.__name__] += 1
            return super().__call__()
        else:
            raise TypeError(f'Limit of {cls.__name__} instances is reached.')


# 6
class FuncBoundedMeta(type):
    amounts = dict()

    def __init__(cls, name, bases, attrs):
        if 'get_max_instance_count' not in attrs \
                or type(attrs['get_max_instance_count']) != classmethod:
            raise TypeError(f'Signature of class {name} is wrong')
        super().__init__(name, bases, attrs)
        cls.amounts[name] = 0

    def __call__(cls, *args, **kwargs):
        if cls.amounts[cls.__name__] < cls.get_max_instance_count():
            cls.amounts[cls.__name__] += 1
            return super().__call__()
        else:
            raise TypeError(f'Limit of {cls.__name__} instances is reached.')


class BoundedBase(metaclass=FuncBoundedMeta):
    @classmethod
    def get_max_instance_count(cls):
        pass


try:
    class BoundedBase2(metaclass=FuncBoundedMeta):
        pass
except TypeError:
    pass
        

class C (metaclass=BoundedMeta, max_instance_count=2):
    pass


class D (metaclass=BoundedMeta, max_instance_count=None):
    pass


class F(BoundedBase):
    @classmethod
    def get_max_instance_count(cls):
        return 1


if __name__ == '__main__':

    c1 = C()
    c2 = C()
    try:
        c3 = C()
    except TypeError:
        print(' everything works fine !')
    else:
        print('something goes wrong !')

    l = []
    for i in range(4):
        l.append(D())

    f1 = F()
    try:
        f2 = F()
    except TypeError:
        print(' everything works fine !')
    else:
        print('something goes wrong !')
