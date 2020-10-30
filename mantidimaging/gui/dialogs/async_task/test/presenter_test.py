import time
import unittest

import mock

from mantidimaging.gui.dialogs.async_task import (AsyncTaskDialogPresenter, AsyncTaskDialogView)
from mantidimaging.gui.dialogs.async_task.presenter import Notification


class AsyncTaskDialogPresenterTest(unittest.TestCase):
    def _long_task(self):
        for ii in range(0, 10):
            time.sleep(1)
        # Shouldn't get here.
        self.assertTrue(False)

    def setUp(self):
        self.v = mock.create_autospec(AsyncTaskDialogView)
        self.p = AsyncTaskDialogPresenter(self.v)

    def test_basic_happy_case(self):
        def f(a, b):
            time.sleep(0.1)
            return a + b

        self.p.set_task(f)
        self.p.set_parameters([5], {'b': 4})
        self.assertFalse(self.p.task_is_running)

        self.p.notify(Notification.START)
        self.v.show.assert_called_once()
        self.assertTrue(self.p.task_is_running)

        self.p.model.task.wait()
        self.assertFalse(self.p.task_is_running)
