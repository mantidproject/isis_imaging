import traceback
from enum import Enum
from logging import getLogger
from typing import List, Tuple, TYPE_CHECKING
from uuid import UUID

from mantidimaging.gui.mvp_base import BasePresenter
from mantidimaging.gui.utility import BlockQtSignals

if TYPE_CHECKING:
    from mantidimaging.gui.widgets.stack_selector import StackSelectorWidgetView


class Notification(Enum):
    RELOAD_STACKS = 0
    SELECT_ELIGIBLE_STACK = 1


class StackSelectorWidgetPresenter(BasePresenter):
    view: 'StackSelectorWidgetView'

    def __init__(self, view):
        super(StackSelectorWidgetPresenter, self).__init__(view)

        self.stack_uuids = []
        self.current_stack = None

    def notify(self, signal):
        try:
            if signal == Notification.RELOAD_STACKS:
                self.do_reload_stacks()
            elif signal == Notification.SELECT_ELIGIBLE_STACK:
                self.do_select_eligible_stack()

        except Exception as e:
            self.show_error(e, traceback.format_exc())
            getLogger(__name__).exception("Notification handler failed")

    def do_reload_stacks(self):
        old_selection = self.view.currentText()
        # Don't want signals emitted when changing the list of stacks
        with BlockQtSignals([self.view]):
            # Clear the previous entries from the drop down menu
            self.view.clear()

            # Get all the new stacks
            stack_list: List[Tuple[UUID, str]] = self.view.main_window.stack_list
            self.stack_uuids, user_friendly_names = \
                zip(*stack_list) if stack_list else (None, [])
            self.view.addItems(user_friendly_names)

            # If the previously selected window still exists with the same name,
            # reselect it, otherwise default to the first item
            if old_selection in user_friendly_names:
                new_selected_index = user_friendly_names.index(old_selection)
            else:
                new_selected_index = 0

            self.view.setCurrentIndex(new_selected_index)

        self.view.stacks_updated.emit()
        self.handle_selection(new_selected_index)

    def handle_selection(self, index):
        self.view.stack_selected_int.emit(index)

        uuid = self.stack_uuids[index] if self.stack_uuids else None
        self.current_stack = uuid
        self.view.stack_selected_uuid.emit(uuid)

    def do_select_eligible_stack(self):
        stack_list: List[Tuple[UUID, str]] = self.view.main_window.stack_list
        for idx, [_, name] in enumerate(stack_list):
            name = name.lower()
            if "dark" not in name and "flat" not in name and "180deg" not in name:
                self.view.setCurrentIndex(idx)
                break
