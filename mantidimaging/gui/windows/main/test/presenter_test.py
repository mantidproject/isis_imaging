import unittest

import mock

from mantidimaging.gui.dialogs.async_task import TaskWorkerThread
from mantidimaging.gui.windows.main import MainWindowView, MainWindowPresenter
from mantidimaging.gui.windows.main.load_dialog.view import MWLoadDialog


class MainWindowPresenterTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MainWindowPresenterTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(MainWindowPresenterTest, self).setUp()

        self.view = mock.create_autospec(MainWindowView)
        self.view.load_dialogue = mock.create_autospec(MWLoadDialog)
        self.presenter = MainWindowPresenter(self.view)

    def test_failed_attempt_to_load_shows_error(self):
        # Create a filed load async task
        task = TaskWorkerThread()
        task.error = 'something'
        self.assertFalse(task.was_successful())

        # Call the callback with a task that failed
        self.presenter._on_stack_load_done(task)

        # Expect error message
        self.view.show_error_dialog.assert_called_once_with(self.presenter.LOAD_ERROR_STRING.format(task.error))

    def test_failed_attempt_to_save_shows_error(self):
        # Create a filed load async task
        task = TaskWorkerThread()
        task.error = 'something'
        self.assertFalse(task.was_successful())

        # Call the callback with a task that failed
        self.presenter._on_save_done(task)

        # Expect error message
        self.view.show_error_dialog.assert_called_once_with(self.presenter.SAVE_ERROR_STRING.format(task.error))


if __name__ == '__main__':
    unittest.main()
