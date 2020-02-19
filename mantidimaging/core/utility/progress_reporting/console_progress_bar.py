import sys

from .progress import ProgressHandler


def _print_ascii_progress_bar(progress, bar_len, prefix='', suffix=''):
    filled_len = int(round(bar_len * progress))

    if prefix:
        prefix = prefix + ': '

    bar = '{}[{}{}]{}'.format(prefix, '=' * filled_len, '-' * (bar_len - filled_len), suffix)

    print(bar, end='\r')
    sys.stdout.flush()


class ConsoleProgressBar(ProgressHandler):
    def __init__(self, width=70):
        super(ConsoleProgressBar, self).__init__()
        self.width = width

    def progress_update(self):
        suffix = '{}/{}'.format(self.progress.current_step, self.progress.end_step)

        _print_ascii_progress_bar(self.progress.completion(), self.width, self.progress.task_name, suffix)

        if self.progress.is_completed():
            print()
