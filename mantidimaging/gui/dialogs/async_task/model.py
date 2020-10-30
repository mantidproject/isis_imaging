from logging import getLogger
from typing import Callable

from PyQt5 import Qt, QtCore

from .task import TaskWorkerThread


class AsyncTaskDialogModel(Qt.QObject):

    # Signal emitted when task processing has terminated
    task_done = QtCore.pyqtSignal(bool)

    def __init__(self):
        super(AsyncTaskDialogModel, self).__init__()

        self.task = TaskWorkerThread()
        self.task.finished.connect(self._on_task_exit)

        self.on_complete_function: Callable = lambda: None

    def do_cancel_task(self):
        try:
            self.task.terminate()
            self.task.wait()
        except Exception as e:
            # This is going to throw
            getLogger(__name__).exception("Terminated thread: " + str(e))

    def do_execute_async(self):
        """
        Start asynchronous execution.
        """
        self.task.start()

    @property
    def task_is_running(self):
        return self.task.isRunning()

    def _on_task_exit(self):
        """
        Handler for task thread completion.

        Forwards task_done signal and calls post processing function (if
        provided).
        """
        log = getLogger(__name__)

        # Emit on complete function
        self.task_done.emit(self.task.was_successful())

        # Call post process function
        if self.on_complete_function is not None:
            try:
                self.on_complete_function(self.task)
            except Exception:
                log.exception("Failed to run task completion callback")
                raise
