import importlib
import sys
import unittest
from io import StringIO
from time import sleep
from unittest import mock

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

    def test_lrucache(self):
        LRUCache = self._load_function(0, 'lru_cache', 'LRUCache')

        cache = LRUCache(size=5, default_ttl=5)
        for i in range(1, 8):
            if not i % 5:
                self.assertEqual(i - 4, cache.get(i - 4))
                if i == 5:
                    self.assertEqual(4, cache.size)
                    self.assertEqual(5, cache.max_size)
            if i == 6:
                self.assertEqual(5, cache.default_ttl)
                cache.default_ttl = 7
                self.assertEqual(7, cache.default_ttl)
            cache.push(i, i)

        self.assertEqual(5, cache.get(5))
        self.assertEqual(6, cache.get(6))
        self.assertEqual(7, cache.get(7))
        self.assertEqual(None, cache.get(0))
        self.assertEqual(None, cache.get(2))
        sleep(5)
        self.assertEqual(None, cache.get(5))
        self.assertEqual(6, cache.get(6))
        sleep(2)
        self.assertEqual(None, cache.get(6))

        cache.clean()
        self.assertEqual(0, cache.size)
        for i in range(1, 20):
            cache.push(i, i, 3)

        for i in range(1, 4):
            cache.pop(20 - i)
        self.assertEqual(cache.size, 2)

        self._check_stdout_empty('mid_skip_queue')


if __name__ == '__main__':
    unittest.main()
