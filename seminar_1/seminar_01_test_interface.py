
import sys
import unittest
import importlib
import collections

from unittest import mock
from io import StringIO


# uncomment the line below and change the path specified
# sys.path.insert(0, r'path_to_solution_folder')
sys.path.insert(0, r'draft')


class InterfaceTestCase(unittest.TestCase):
    def setUp(self):
        self._stdout_mock = self._setup_stdout_mock()

    def _setup_stdout_mock(self):
        patcher = mock.patch('sys.stdout', new=StringIO())
        patcher.start()
        self.addCleanup(patcher.stop)
        return patcher.new

    def _check_stdout_empty(self, file_name):
        if self._stdout_mock is not None:
            self.assertFalse(self._stdout_mock.getvalue(),
                             'no prints to console are allowed in "%s"' % file_name)
                             
    def _load_task(self, task_idx, file_name):
        try:
            loaded_task = importlib.import_module(file_name)
        except ImportError:
            self.fail('cannot import task #%d solution - no file "%s"' % (task_idx, file_name))
        return loaded_task
                             
    def _load_function(self, task_idx, file_name, func_names):
        loaded_task = self._load_task(task_idx, file_name)

        func_names = (func_names, ) if isinstance(func_names, str) else func_names
        loaded_functions = list(filter(None, (getattr(loaded_task, func_name, None) for func_name in func_names)))

        self.assertEqual(1, len(loaded_functions),
                         'cannot import task #%d solution - only one of function(-s) "%s" must be in file "%s"'
                         % (task_idx, file_name, func_names))

        return loaded_functions[0]

    def test_fizzbuzz(self):
        self._load_task(0, 'fizzbuzz')
        
    def test_thue_morse(self):
        f = self._load_function(1, 'thue_morse', 'get_sequence_item')

        self.assertEqual(0b0, f(0))
        self.assertEqual(0b1, f(1))
        self.assertEqual(0b110, f(2))
        self.assertEqual(0b1101001, f(3))

        self._check_stdout_empty('thue_morse')

    def test_exchange(self):
        f = self._load_function(2, 'ticket', 'get_nearest_lucky_ticket')

        self.assertEqual(111111, f(111111))
        self.assertEqual(123321, f(123322))
        self.assertEqual(123321, f(123320))
        self.assertEqual(334019, f(333999))

        self._check_stdout_empty('ticket')

    def test_sort(self):
        f = self._load_function(3, 'merge', 'merge')

        self.assertIsInstance(f([1], [2]), list)
        self.assertIsInstance(f((1, ), (2, )), tuple)

        self.assertSequenceEqual([1, 2, 3, 7], f([1, 2, 7], [3]))
        self.assertSequenceEqual((3, 7, 8, 15), f((3, 15), (7, 8)))

        self._check_stdout_empty('merge')


if __name__ == '__main__':
    unittest.main()
