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
            self.fail('cannot import task #%d solution - no file "%s"' % (
            task_idx, file_name))
        return loaded_task

    def _load_function(self, task_idx, file_name, func_names):
        loaded_task = self._load_task(task_idx, file_name)

        func_names = (func_names,) if isinstance(func_names,
                                                 str) else func_names
        loaded_functions = list(filter(None,
                                       (getattr(loaded_task, func_name, None)
                                        for func_name in func_names)))

        self.assertEqual(1, len(loaded_functions),
                         'cannot import task #%d solution - only one of function(-s) "%s" must be in file "%s"'
                         % (task_idx, file_name, func_names))

        return loaded_functions[0]

    def test_mid_skip_queue(self):
        MidSkipQueue = self._load_function(0, 'mid_skip_queue', 'MidSkipQueue')
        self.assertEqual([1, 2, 3, 6, 7, 8],
                         MidSkipQueue(3, (1, 2, 3, 4, 5, 6, 7, 8)).list)

        q = MidSkipQueue(1)
        q.append(-1)
        q += (-2, -3)
        self.assertEqual([-1, -3], q.list)
        q.append(4)
        self.assertEqual([-1, 4], q.list)
        q.append(5)
        self.assertEqual([-1, 5], q.list)
        self.assertEqual(5, q[1])
        self.assertEqual(1, q.index(5))
        self.assertEqual(-1, q.index(55))
        q.append(6, 7)
        self.assertEqual([-1, 7], q.list)

        q = MidSkipQueue(2, "Hello!")
        self.assertEqual(['H', 'e', 'o', '!'], q.list)

        self._check_stdout_empty('mid_skip_queue')

    def test_mid_skip_priority_queue(self):
        MidSkipPriorityQueue = self._load_function(0, 'mid_skip_queue', 'MidSkipPriorityQueue')

        self._check_stdout_empty('mid_skip_queue')


if __name__ == '__main__':
    unittest.main()
