import threading
import time
from logging import getLogger

from mantidimaging.core.utility.memory_usage import get_memory_usage_linux_str


class ProgressHandler(object):
    def __init__(self):
        self.progress = None

    def progress_update(self):
        raise NotImplementedError("Need to implement this method in the child class")


class Progress(object):
    """
    Class used to perform basic progress monitoring and reporting.
    """
    @staticmethod
    def ensure_instance(p=None, *args, **kwargs):
        """
        Helper function used to select either a non-None Progress instance as a
        parameter, or simply create and configure a new one.
        """
        if not p:
            p = Progress(*args, **kwargs)
            from .console_progress_bar import ConsoleProgressBar
            p.add_progress_handler(ConsoleProgressBar())

        return p

    def __init__(self, num_steps=1, task_name='Task'):
        self.task_name = task_name

        # Estimated number of steps (used to calculated percentage complete)
        self.end_step = 0
        self.set_estimated_steps(num_steps)

        # Current step being executed (0 denoting not started)
        self.current_step = 0

        # Flag indicating completion
        self.complete = False

        # List of tuples defining progress history
        # (timestamp, step, message)
        self.progress_history = []

        # Lock used to synchronise modifications to the progress state
        self.lock = threading.Lock()

        # Handers that receive notifications when progress updates occur
        self.progress_handlers = []

        # Levels of nesting when used as a context manager
        self.context_nesting_level = 0

        # Flag to indicate cancellation of the current task
        self.cancel_msg = None

        # Add initial step to history
        self.update(0, 'init')

        # Log initial memory usage
        getLogger(__name__).debug("Memory usage before execution: %s", get_memory_usage_linux_str())

    def __str__(self):
        return 'Progress(\n{})'.format('\n'.join(self.progress_history))

    def __enter__(self):
        self.context_nesting_level += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context_nesting_level -= 1

        # Only when we have left the context at all levels is the task complete
        if self.context_nesting_level == 0:
            self.mark_complete()

    def is_started(self):
        """
        Checks if the task has been started.

        A task starts when it reports it's first progress update.
        """
        return self.current_step > 0

    def is_completed(self):
        """
        Checks if the task has been marked as completed.
        """
        return self.complete

    def completion(self):
        """
        Gets the completion of the task in the range of 0.0 - 1.0
        """
        with self.lock:
            return round(self.current_step / self.end_step, 3)

    def last_status_message(self):
        """
        Gets the message from the last progress update.
        """
        with self.lock:
            if len(self.progress_history) > 0:
                msg = self.progress_history[-1][2]
                return msg if len(msg) > 0 else None

        return None

    def execution_time(self):
        """
        Gets the total time this task has been executing.

        Total time is measured from the timestamp of the first progress message
        to the timestamp of the last progress message.
        """
        if len(self.progress_history) > 2:
            start = self.progress_history[1][0]
            last = self.progress_history[-1][0]
            return last - start
        else:
            return 0.0

    def set_estimated_steps(self, num_steps):
        """
        Sets the number of steps this task is expected to take to complete.
        """
        self.end_step = num_steps

    def add_estimated_steps(self, num_steps):
        """
        Increments the number of steps this task is expected to take to
        complete.
        """
        self.end_step += num_steps

    def add_progress_handler(self, handler):
        """
        Adds a handler to receiver progress updates.
        :param handler: Instance of a progress handler
        """
        if not isinstance(handler, ProgressHandler):
            raise ValueError("Progress handlers must be of type ProgressHandler")

        self.progress_handlers.append(handler)
        handler.progress = self

    def update(self, steps=1, msg='', force_continue=False):
        """
        Updates the progress of the task.

        :param steps: Number of steps that have been completed since last call
                      to this function
        :param msg: Message describing current step
        """
        # Acquire lock while manipulating progress state
        with self.lock:
            # Update current step
            self.current_step += steps
            if self.current_step > self.end_step:
                self.end_step = self.current_step + 1

            # Update progress history
            step_details = (time.clock(), self.current_step, msg)
            self.progress_history.append(step_details)

        # Process progress callbacks
        if len(self.progress_handlers) != 0:
            for cb in self.progress_handlers:
                cb.progress_update()

        # Force cancellation on progress update
        if self.should_cancel and not force_continue:
            raise RuntimeError('Task has been cancelled')

    def cancel(self, msg='cancelled'):
        """
        Mark the task tree that uses this progress instance for cancellation.

        Task should either periodically inspect should_cancel or have suitably
        many calls to update() to be cancellable.
        """
        self.cancel_msg = msg

    @property
    def should_cancel(self):
        """
        Checks if the task should be cancelled.
        """
        return self.cancel_msg is not None

    def mark_complete(self, msg='complete'):
        """
        Marks the task as completed.
        """
        log = getLogger(__name__)

        self.update(force_continue=True, msg=self.cancel_msg if self.should_cancel else msg)

        if not self.should_cancel:
            self.complete = True
            self.end_step = self.current_step

        # Log elapsed time and final memory usage
        log.info("Elapsed time: %d sec.", self.execution_time())
        log.debug("Memory usage after execution: %s", get_memory_usage_linux_str())
