import unittest

from mantidimaging.gui.dialogs.async_task.task import TaskWorkerThread


class TaskWorkerThreadTest(unittest.TestCase):
    def test_basic_happy_case(self):
        def f(a, b):
            return a + b

        t = TaskWorkerThread()
        t.task_function = f
        t.kwargs = {'a': 5, 'b': 4}

        t.run()

        t.wait()

        self.assertTrue(t.was_successful())
        self.assertIsNone(t.error)
        self.assertEquals(t.result, 9)

    def test_failure(self):
        def f(a, b):
            raise RuntimeError('nope')

        t = TaskWorkerThread()
        t.task_function = f
        t.kwargs = {'a': 5, 'b': 4}

        t.run()

        t.wait()

        self.assertFalse(t.was_successful())
        self.assertIsNotNone(t.error)
        self.assertIsNone(t.result)

        self.assertTrue(isinstance(t.error, RuntimeError))
        self.assertEquals(t.error.args, ('nope', ))
