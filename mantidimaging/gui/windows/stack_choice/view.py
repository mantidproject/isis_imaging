from enum import Enum, auto

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy, QMessageBox
from pyqtgraph import ViewBox

from mantidimaging.gui.widgets.pg_image_view import MIImageView

from mantidimaging.gui.mvp_base import BaseMainWindowView


class Notification(Enum):
    CHOOSE_ORIGINAL = auto()
    CHOOSE_NEW_DATA = auto()


class StackChoiceView(BaseMainWindowView):
    def __init__(self, original_stack, new_stack, presenter):
        super(StackChoiceView, self).__init__(presenter.operations_presenter.view, "gui/ui/stack_choice_window.ui")

        self.presenter = presenter

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Choose the stack you want to keep")
        self.setWindowModality(Qt.ApplicationModal)

        # Create stacks and place them in the choice window
        self.original_stack = MIImageView(detailsSpanAllCols=True)
        self.original_stack.name = "Original Stack"

        self.new_stack = MIImageView(detailsSpanAllCols=True)
        self.new_stack.name = "New Stack"

        self._setup_stack_for_view(self.original_stack, original_stack.data)
        self._setup_stack_for_view(self.new_stack, new_stack.data)

        self.topHorizontalLayout.insertWidget(0, self.original_stack)
        self.topHorizontalLayout.addWidget(self.new_stack)

        self.shifting_through_images = False
        self.original_stack.sigTimeChanged.connect(self._sync_timelines_for_new_stack_with_old_stack)
        self.new_stack.sigTimeChanged.connect(self._sync_timelines_for_old_stack_with_new_stack)

        # Hook nav buttons into original stack (new stack not needed as the timelines are synced)
        self.leftButton.pressed.connect(self.original_stack.button_stack_left.pressed)
        self.leftButton.released.connect(self.original_stack.button_stack_left.released)
        self.rightButton.pressed.connect(self.original_stack.button_stack_right.pressed)
        self.rightButton.released.connect(self.original_stack.button_stack_right.released)

        # Hook the choice buttons
        self.originalDataButton.clicked.connect(lambda: self.presenter.notify(Notification.CHOOSE_ORIGINAL))
        self.newDataButton.clicked.connect(lambda: self.presenter.notify(Notification.CHOOSE_NEW_DATA))

        # Hook ROI button into both stacks
        self.roiButton.clicked.connect(self._toggle_roi)

        # Hook the two plot ROIs together so that any changes are synced
        self.original_stack.roi.sigRegionChanged.connect(self._sync_roi_plot_for_new_stack_with_old_stack)
        self.new_stack.roi.sigRegionChanged.connect(self._sync_roi_plot_for_old_stack_with_new_stack)

        self._sync_both_image_axis()

        self.choice_made = False
        self.roi_shown = False

    def _toggle_roi(self):
        if self.roi_shown:
            self.roi_shown = False
            self.original_stack.ui.roiBtn.setChecked(False)
            self.new_stack.ui.roiBtn.setChecked(False)
            self.original_stack.roiClicked()
            self.new_stack.roiClicked()
        else:
            self.roi_shown = True
            self.original_stack.ui.roiBtn.setChecked(True)
            self.new_stack.ui.roiBtn.setChecked(True)
            self.original_stack.roiClicked()
            self.new_stack.roiClicked()

    def _setup_stack_for_view(self, stack, data):
        stack.setContentsMargins(4, 4, 4, 4)
        stack.setImage(data)
        stack.ui.menuBtn.hide()
        stack.ui.roiBtn.hide()
        stack.button_stack_right.hide()
        stack.button_stack_left.hide()
        details_size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        details_size_policy.setHorizontalStretch(1)
        stack.details.setSizePolicy(details_size_policy)
        self.roiButton.clicked.connect(stack.roiClicked)

    def _sync_roi_plot_for_new_stack_with_old_stack(self):
        self.new_stack.roi.sigRegionChanged.disconnect(self._sync_roi_plot_for_old_stack_with_new_stack)
        self.new_stack.roi.setPos(self.original_stack.roi.pos())
        self.new_stack.roi.setSize(self.original_stack.roi.size())
        self.new_stack.roi.sigRegionChanged.connect(self._sync_roi_plot_for_old_stack_with_new_stack)

    def _sync_roi_plot_for_old_stack_with_new_stack(self):
        self.original_stack.roi.sigRegionChanged.disconnect(self._sync_roi_plot_for_new_stack_with_old_stack)
        self.original_stack.roi.setPos(self.new_stack.roi.pos())
        self.original_stack.roi.setSize(self.new_stack.roi.size())
        self.original_stack.roi.sigRegionChanged.connect(self._sync_roi_plot_for_new_stack_with_old_stack)

    def _sync_timelines_for_new_stack_with_old_stack(self, index, _):
        self.new_stack.sigTimeChanged.disconnect(self._sync_timelines_for_old_stack_with_new_stack)
        self.new_stack.setCurrentIndex(index)
        self.new_stack.sigTimeChanged.connect(self._sync_timelines_for_old_stack_with_new_stack)

    def _sync_timelines_for_old_stack_with_new_stack(self, index, _):
        self.original_stack.sigTimeChanged.disconnect(self._sync_timelines_for_new_stack_with_old_stack)
        self.original_stack.setCurrentIndex(index)
        self.original_stack.sigTimeChanged.connect(self._sync_timelines_for_new_stack_with_old_stack)

    def _sync_both_image_axis(self):
        self.original_stack.view.linkView(ViewBox.XAxis, self.new_stack.view)
        self.original_stack.view.linkView(ViewBox.YAxis, self.new_stack.view)

    def closeEvent(self, e):
        # Confirm exit is actually wanted as it will lead to data loss
        if not self.choice_made:
            response = QMessageBox.warning(self, "Data Loss! Are you sure?",
                                           "You will lose the original stack if you close this window! Are you sure?",
                                           QMessageBox.Ok | QMessageBox.Cancel)
            if response == QMessageBox.Ok:
                self.presenter.notify(Notification.CHOOSE_NEW_DATA)
            else:
                e.ignore()
                return
        self.original_stack.close()
        self.new_stack.close()
