from enum import Enum, _EnumDict, _is_descriptor
from types import DynamicClassAttribute


class auto:
   value = object()


class _FlagDict(dict):
    def __init__(self):
        super().__init__()
        self._member_names = []

    def __setitem__(self, key, value):
        if key == '_generate_next_value_':
            setattr(self, '_generate_next_value', value)
        elif key in self._member_names:
            raise TypeError('Attempted to reuse key: %r' % key)
        elif not _is_descriptor(value):
            if key in self:
                raise TypeError('%r already defined as: %r' % (key, self[key]))
            if isinstance(value, auto):
                if value.value == object():
                    value.value = self._generate_flag_value(key)
                value = value.value
            self._member_names.append(key)
        super().__setitem__(key, value)


class FlagMeta(type):
    @classmethod
    def __prepare__(metacls, cls, bases):
        flag_dict = _FlagDict()
        return flag_dict

    def __new__(mcs, cls, bases, classdict):

        enum_members = {k: classdict[k] for k in classdict._member_names}

    def __setattr__(self, name, value):
        if callable(value):
            super(FlagMeta, self).__setattr__(name, value)
        elif name != '_member_map_':
            if isinstance(value, auto):
                if value.value == object():
                    value.value = self._generate_flag_value(
                        name)
                value = value.value
            # self._member_names.append(key)
            self._member_map_[name] = value

    def __getattr__(cls, name):
        try:
            return cls._member_map_[name]
        except KeyError:
            raise AttributeError(name) from None


class Flag(metaclass=FlagMeta):

    @staticmethod
    def _pows_generator():
        i = 0
        while True:
            yield 2 ** i
            i += 1

    def _generate_flag_value(self, name):
        cls = self.__class__
        values = cls._member_map_.values()
        for i in self._pows_generator():
            if i not in values:
                cls._member_map_[name] = i
                break

    @DynamicClassAttribute
    def name(self):
        """The name of the Enum member."""
        return self._name_

    @DynamicClassAttribute
    def value(self):
        """The value of the Enum member."""
        return self._value_

    def __or__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self._value_ | other._value_)

    def __and__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self._value_ & other._value_)


class MyFlag(Flag):
    first = auto()
    second = auto()
    third = 4





if __name__ == '__main__':
    m = MyFlag()
