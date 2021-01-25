# Copyright (C) 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later

import os
import unittest
from pathlib import Path
from tempfile import mkdtemp
from uuid import uuid4

from PyQt5.QtWidgets import QMainWindow, QMenu, QWidget, QApplication

from mantidimaging.core.io.loader import loader
from mantidimaging.eyes_tests.eyes_manager import EyesManager
from mantidimaging.test_helpers.start_qapplication import start_qapplication

# APPLITOOLS_BATCH_ID will be set by Github actions to the commit SHA, or a random UUID for individual developer
# execution
APPLITOOLS_BATCH_ID = os.getenv("APPLITOOLS_BATCH_ID")
if APPLITOOLS_BATCH_ID is None:
    APPLITOOLS_BATCH_ID = uuid4()

API_KEY_PRESENT = os.getenv("APPLITOOLS_API_KEY")
if API_KEY_PRESENT is None:
    raise unittest.SkipTest("API Key is not defined in the environment, so Eyes tests are skipped.")


@start_qapplication
class BaseEyesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.eyes_manager = EyesManager("Mantid Imaging")
        cls.eyes_manager.set_batch(APPLITOOLS_BATCH_ID)

    def setUp(self):
        self.imaging = None
        self.eyes_manager.image_directory = mkdtemp()

        # Do setup
        self.eyes_manager.start_imaging()

    def tearDown(self):
        if self.imaging is not None:
            self.eyes_manager.close_imaging()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.eyes_manager.close_eyes()

    @property
    def imaging(self):
        return self.eyes_manager.imaging

    @imaging.setter
    def imaging(self, imaging):
        self.eyes_manager.imaging = imaging

    def check_target(self, image=None, widget: QWidget = None):
        self.eyes_manager.check_target(image, widget)

    @staticmethod
    def show_menu(widget: QMainWindow, menu: QMenu):
        menu_location = widget.menuBar().rect().bottomLeft()
        menu.popup(widget.mapFromGlobal(menu_location))

    def _load_data_set(self):
        dataset = loader.load(file_names=
                              [str(Path.home())
                               + "/mantidimaging-data/ISIS/IMAT/IMAT00010675/Tomo/IMAT_Flower_Tomo_000000.tif"])
        self.imaging.presenter.create_new_stack(dataset, "Stack 1")

        QApplication.processEvents()