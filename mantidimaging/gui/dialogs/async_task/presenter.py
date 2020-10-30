from logging import getLogger
from enum import Enum, auto
from PyQt5 import Qt

from mantidimaging.core.utility.progress_reporting import ProgressHandler

from .model import AsyncTaskDialogModel


class Notification(Enum):
    START = auto()
    CANCEL = auto()


class AsyncTaskDialogPresenter(Qt.QObject, ProgressHandler):
    progress_updated = Qt.pyqtSignal(float, str)

    def __init__(self, view):
        super(AsyncTaskDialogPresenter, self).__init__()

        self.view = view
        self.progress_updated.connect(self.view.set_progress)

        self.model = AsyncTaskDialogModel()
        self.model.task_done.connect(self.view.handle_completion)

    def notify(self, signal):
        try:
            if signal == Notification.START:
                self.do_start_processing()
            elif signal == Notification.CANCEL:
                self.do_cancel_processing()
        except Exception as e:
            getLogger(__name__).exception("Notification handler failed: " + str(e))

    def do_cancel_processing(self):
        # Ensure the user is sure this is what they want to do
        if self.view.ask_user_if_they_are_sure_destructive():
            self.model.do_cancel_task()

    def set_task(self, f):
        self.model.task.task_function = f

    def set_parameters(self, *args, **kwargs):
        self.model.task.args = args
        self.model.task.kwargs = kwargs

    def set_on_complete(self, f):
        self.model.on_complete_function = f

    def do_start_processing(self):
        """
        Starts async task execution and shows GUI.
        """
        self.model.do_execute_async()
        self.view.show()

    @property
    def task_is_running(self):
        return self.model.task_is_running

    def progress_update(self):
        msg = self.progress.last_status_message()
        self.progress_updated.emit(self.progress.completion(), msg if msg is not None else '')
