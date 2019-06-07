from logging import getLogger

import matplotlib
from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from mantidimaging.gui.mvp_base import BaseMainWindowView
from mantidimaging.gui.windows.cor_tilt import CORTiltWindowView
from mantidimaging.gui.windows.filters import FiltersWindowView
from mantidimaging.gui.windows.main.load_dialog import MWLoadDialog
from mantidimaging.gui.windows.main.presenter import MainWindowPresenter
from mantidimaging.gui.windows.main.presenter import Notification as PresNotification
from mantidimaging.gui.windows.main.save_dialog import MWSaveDialog
from mantidimaging.gui.windows.savu_filters.view import SavuFiltersWindowView
from mantidimaging.gui.windows.stack_visualiser import StackVisualiserView
from mantidimaging.gui.windows.tomopy_recon import TomopyReconWindowView


class MainWindowView(BaseMainWindowView):
    active_stacks_changed = Qt.pyqtSignal()

    def __init__(self):
        super(MainWindowView, self).__init__(None, 'gui/ui/main_window.ui')

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("MantidImaging")

        self.presenter = MainWindowPresenter(self)

        self.setup_shortcuts()
        self.update_shortcuts()

    def setup_shortcuts(self):
        self.actionLoad.triggered.connect(self.show_load_dialogue)
        self.actionSave.triggered.connect(self.show_save_dialogue)
        self.actionExit.triggered.connect(self.close)

        self.actionOnlineDocumentation.triggered.connect(
            self.open_online_documentation)
        self.actionAbout.triggered.connect(self.show_about)

        self.actionCorTilt.triggered.connect(self.show_cor_tilt_window)
        self.actionImageOperations.triggered.connect(self.show_filters_window)
        self.actionSavuImageOperations.triggered.connect(self.show_savu_filters_window)
        self.actionTomopyRecon.triggered.connect(self.show_tomopy_recon_window)

        self.active_stacks_changed.connect(self.update_shortcuts)

    def update_shortcuts(self):
        self.actionSave.setEnabled(len(self.presenter.stack_names()) > 0)

    def open_online_documentation(self):
        url = QtCore.QUrl('https://mantidproject.github.io/mantidimaging/')
        QtGui.QDesktopServices.openUrl(url)

    def show_about(self):
        from mantidimaging import __version__ as version_no
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("About MantidImaging")
        msg_box.setTextFormat(QtCore.Qt.RichText)
        msg_box.setText(
            '<a href="https://github.com/mantidproject/mantidimaging">MantidImaging</a>' \
            '<br>Version: <a href="https://github.com/mantidproject/mantidimaging/releases/tag/{0}">{0}</a>'.format(
                version_no))
        msg_box.show()

    def show_load_dialogue(self):
        self.load_dialogue = MWLoadDialog(self)
        self.load_dialogue.show()

    def execute_save(self):
        self.presenter.notify(PresNotification.SAVE)

    def execute_load(self):
        self.presenter.notify(PresNotification.LOAD)

    def show_save_dialogue(self):
        self.save_dialogue = MWSaveDialog(self, self.stack_list())
        self.save_dialogue.show()

    def show_cor_tilt_window(self):
        CORTiltWindowView(self).show()

    def show_filters_window(self):
        FiltersWindowView(self).show()

    def show_savu_filters_window(self):
        SavuFiltersWindowView(self).show()

    def show_tomopy_recon_window(self):
        TomopyReconWindowView(self).show()

    def stack_list(self):
        return self.presenter.stack_list()

    def stack_names(self):
        return self.presenter.stack_names()

    def stack_uuids(self):
        return self.presenter.stack_uuids()

    def get_stack_visualiser(self, stack_uuid):
        return self.presenter.get_stack_visualiser(stack_uuid)

    def create_stack_window(self,
                            stack,
                            title,
                            position=QtCore.Qt.TopDockWidgetArea,
                            floating=False):
        dock_widget = Qt.QDockWidget(title, self)

        # this puts the new stack window into the centre of the window
        self.setCentralWidget(dock_widget)

        # add the dock widget into the main window
        self.addDockWidget(position, dock_widget)

        # we can get the stack visualiser widget with dock_widget.widget
        dock_widget.setWidget(
            StackVisualiserView(self, dock_widget, stack))

        # proof of concept above
        assert isinstance(
            dock_widget.widget(), StackVisualiserView
        ), "Widget inside dock_widget is not an StackVisualiserView!"

        dock_widget.setFloating(floating)

        return dock_widget

    def remove_stack(self, obj):
        getLogger(__name__).debug("Removing stack with uuid %s", obj.uuid)
        self.presenter.remove_stack(obj.uuid)

    def closeEvent(self, event):
        """
        Handles a request to quit the application from the user.
        """
        should_close = True

        if self.presenter.have_active_stacks:
            # Show confirmation box asking if the user really wants to quit if
            # they have data loaded
            msg_box = QtWidgets.QMessageBox.question(
                self,
                "Quit",
                "Are you sure you want to quit?",
                defaultButton=QtWidgets.QMessageBox.No)
            should_close = msg_box == QtWidgets.QMessageBox.Yes

        if should_close:
            # Close all matplotlib PyPlot windows when exiting.
            getLogger(__name__).debug("Closing all PyPlot windows")
            matplotlib.pyplot.close("all")

            # Pass close event to parent
            super(MainWindowView, self).closeEvent(event)

        else:
            # Ignore the close event, keeping window open
            event.ignore()
