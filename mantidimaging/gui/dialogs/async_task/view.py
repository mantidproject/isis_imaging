from typing import Callable

from PyQt5.QtWidgets import QMessageBox

from mantidimaging.core.utility.progress_reporting import Progress
from mantidimaging.gui.mvp_base import BaseDialogView
from .presenter import AsyncTaskDialogPresenter, Notification

from PyQt5 import Qt


class AsyncTaskDialogView(BaseDialogView):
    def __init__(self, parent: 'Qt.QMainWindow', auto_close=False):
        super(AsyncTaskDialogView, self).__init__(parent, 'gui/ui/async_task_dialog.ui')

        self.parent_view = parent
        self.presenter = AsyncTaskDialogPresenter(self)
        self.auto_close = auto_close

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1000)

        self.progress_text = self.infoText.text()

    def reject(self):
        if not self.presenter.task_is_running:
            super(AsyncTaskDialogView, self).reject()
        else:
            self.presenter.notify(Notification.CANCEL)

    def handle_completion(self, successful):
        """
        Updates the UI after the task has been completed.

        :param successful: If the task was successful
        """
        if successful:
            # Set info text to "Complete"
            self.infoText.setText("Complete")
        else:
            self.infoText.setText("Task failed.")

        # If auto close is enabled and the task was successful then hide the UI
        if self.auto_close:
            self.hide()

    def set_progress(self, progress, message):
        # Set status message
        if message:
            self.infoText.setText(message)

        # Update progress bar
        self.progressBar.setValue(progress * 1000)

    def ask_user_if_they_are_sure_destructive(self):
        response = QMessageBox.warning(
            self, "Destructive Action",
            "Cancelling a task in progress has the potential to cause unknown side effects, "
            "and destroy data, are you sure?", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        return response == QMessageBox.Yes


def start_async_task_view(parent: 'Qt.QMainWindow', task: Callable, on_complete: Callable, kwargs=None):
    atd = AsyncTaskDialogView(parent, auto_close=True)
    if not kwargs:
        kwargs = {'progress': Progress()}
    else:
        kwargs['progress'] = Progress()
    kwargs['progress'].add_progress_handler(atd.presenter)

    atd.presenter.set_task(task)
    atd.presenter.set_on_complete(on_complete)
    atd.presenter.set_parameters(**kwargs)
    atd.presenter.do_start_processing()
