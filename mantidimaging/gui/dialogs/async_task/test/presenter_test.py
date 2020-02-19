import time
import unittest

import mock

from mantidimaging.gui.dialogs.async_task import (AsyncTaskDialogPresenter, AsyncTaskDialogView)
from mantidimaging.gui.dialogs.async_task.presenter import Notification


class AsyncTaskDialogPresenterTest(unittest.TestCase):
    def test_basic_happy_case(self):
        def f(a, b):
            time.sleep(0.1)
            return a + b

        v = mock.create_autospec(AsyncTaskDialogView)

        p = AsyncTaskDialogPresenter(v)
        p.set_task(f)
        p.set_parameters([5], {'b': 4})
        self.assertFalse(p.task_is_running)

        p.notify(Notification.START)
        v.show.assert_called_once()
        self.assertTrue(p.task_is_running)

        p.model.task.wait()
        self.assertFalse(p.task_is_running)
