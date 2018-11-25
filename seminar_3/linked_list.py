
class Node:
    def __init__(self, value, next_=None):
        assert isinstance(next_, (Node, type(None))), (
            'The `next_` argument must be an instance of '
            '`Node`, not `{}.{}`.'.format(
                next_.__class__.__module__, next_.__class__.__name__)
        )

        self._value = value
        self._next = next_

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, next_):
        assert isinstance(next_, (Node, type(None))), (
            'The `next_` argument must be an instance of '
            '`Node`, not `{}.{}`.'.format(
                next_.__class__.__module__, next_.__class__.__name__)
        )

        self._next = next_

    def __iter__(self):
        x = self
        while x:
            yield x
            x = x.next

    def __str__(self):
        return f'value: {self.value} | next: [{self.next}]'


def flatten_linked_list(linked_list):
    new_list = []
    for node in linked_list:
        if isinstance(node.value, Node):
            new_list.extend(flatten_linked_list(node.value))
        else:
            new_list.append(node.value)
    return new_list


if __name__ == '__main__':
    r1 = Node(1)  # 1 -> None - just one node
    r2 = Node(7, Node(2, Node(9)))  # 7 -> 2 -> 9 -> None
    # for r in r2:
    #     print(r)
    # 3 -> (19 -> 25 -> None ) -> 12 -> None
    r3 = Node(3, Node(Node(19, Node(25)), Node(12)))
    # for r in r3:
    #     print(r)
    r3_flattenned = flatten_linked_list(r3)  # 3 -> 19 -> 25 -> 12 -> None
    print('\n')
    # for r in r3_flattenned:
    #     print(r)
    r3_expected_flattenned_collection = [3, 19, 25, 12]
    assert r3_expected_flattenned_collection == list(r3_flattenned)
