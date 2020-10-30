import time
import unittest

import mock

from mantidimaging.gui.dialogs.async_task import AsyncTaskDialogModel


class AsyncTaskDialogModelTest(unittest.TestCase):
    def setUp(self):
        done_func = mock.MagicMock()
        self.m = AsyncTaskDialogModel()
        self.m.on_complete_function = done_func

    def test_basic_happy_case(self):
        def f(a, b):
            time.sleep(0.1)
            return a + b

        self.m.task.task_function = f
        self.m.task.kwargs = {'a': 5, 'b': 4}
        self.assertFalse(self.m.task_is_running)

        self.m.do_execute_async()
        self.assertTrue(self.m.task_is_running)

        self.m.task.wait()
        self.assertFalse(self.m.task_is_running)

    def test_async_task_cancelled(self):
        def long_task():
            for ii in range(0, 100):
                time.sleep(0.1)
            # Should not get here
            self.assertFalse(True)

        self.m.task.task_function = long_task
        self.assertFalse(self.m.task_is_running)

        self.m.do_execute_async()
        self.assertTrue(self.m.task_is_running)

        self.m.do_cancel_task()
        self.assertFalse(self.m.task_is_running)
