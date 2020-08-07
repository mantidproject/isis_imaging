import traceback
from enum import Enum, auto
from logging import getLogger
from typing import TYPE_CHECKING, Dict, List

from PyQt5.QtWidgets import QWidget

from mantidimaging.core.utility.data_containers import ScalarCoR, Degrees
from mantidimaging.gui.dialogs.async_task import start_async_task_view, TaskWorkerThread
from mantidimaging.gui.dialogs.cor_inspection.view import CORInspectionDialogView
from mantidimaging.gui.mvp_base import BasePresenter
from mantidimaging.gui.utility.qt_helpers import BlockQtSignals
from mantidimaging.gui.windows.recon.model import ReconstructWindowModel

LOG = getLogger(__name__)

if TYPE_CHECKING:
    from mantidimaging.gui.windows.recon.view import ReconstructWindowView


class AutoCorMethod(Enum):
    CORRELATION = auto()
    MINIMISATION_SQUARE_SUM = auto()


class Notifications(Enum):
    RECONSTRUCT_VOLUME = auto()
    RECONSTRUCT_SLICE = auto()
    RECONSTRUCT_USER_CLICK = auto()
    COR_FIT = auto()
    CLEAR_ALL_CORS = auto()
    REMOVE_SELECTED_COR = auto()
    CALCULATE_CORS_FROM_MANUAL_TILT = auto()
    ALGORITHM_CHANGED = auto()
    UPDATE_PROJECTION = auto()
    ADD_COR = auto()
    REFINE_COR = auto()
    AUTO_FIND_COR = auto()


class ReconstructWindowPresenter(BasePresenter):
    ERROR_STRING = "COR/Tilt finding failed: {}"
    view: 'ReconstructWindowView'
    _ignore_stack_change: bool = False

    def __init__(self, view: 'ReconstructWindowView', main_window):
        super(ReconstructWindowPresenter, self).__init__(view)
        self.view = view
        self.model = ReconstructWindowModel(self.view.cor_table_model)
        self.allowed_recon_kwargs: Dict[str, List[str]] = self.model.load_allowed_recon_kwargs()
        self.restricted_arg_widgets: Dict[str, List[QWidget]] = {
            'filter_name': [self.view.filterName, self.view.filterNameLabel],
            'num_iter': [self.view.numIter, self.view.numIterLabel],
        }
        self.main_window = main_window

    def notify(self, notification, slice_idx=None):
        try:
            if notification == Notifications.RECONSTRUCT_VOLUME:
                self.do_reconstruct_volume()
            elif notification == Notifications.RECONSTRUCT_SLICE:
                self.do_reconstruct_slice()
            elif notification == Notifications.RECONSTRUCT_USER_CLICK:
                self.do_reconstruct_slice(slice_idx=slice_idx)
            elif notification == Notifications.COR_FIT:
                self.do_cor_fit()
            elif notification == Notifications.CLEAR_ALL_CORS:
                self.do_clear_all_cors()
            elif notification == Notifications.REMOVE_SELECTED_COR:
                self.do_remove_selected_cor()
            elif notification == Notifications.CALCULATE_CORS_FROM_MANUAL_TILT:
                self.do_calculate_cors_from_manual_tilt()
            elif notification == Notifications.ALGORITHM_CHANGED:
                self.do_algorithm_changed()
            elif notification == Notifications.UPDATE_PROJECTION:
                self.do_update_projection()
            elif notification == Notifications.ADD_COR:
                self.do_add_cor()
            elif notification == Notifications.REFINE_COR:
                self._do_refine_selected_cor()
            elif notification == Notifications.AUTO_FIND_COR:
                self.do_auto_find_cor()
        except Exception as err:
            self.show_error(err, traceback.format_exc())

    def do_algorithm_changed(self):
        alg_name = self.view.algorithm_name
        allowed_args = self.allowed_recon_kwargs[alg_name]
        for arg, widgets in self.restricted_arg_widgets.items():
            if arg in allowed_args:
                for widget in widgets:
                    widget.show()
            else:
                for widget in widgets:
                    widget.hide()
        with BlockQtSignals([self.view.filterName, self.view.numIter]):
            self.view.set_filters_for_recon_tool(self.model.get_allowed_filters(alg_name))
        self.do_reconstruct_slice()

    def set_stack_uuid(self, uuid):
        stack = self.view.get_stack_visualiser(uuid)
        if self.model.is_current_stack(stack):
            return

        self.view.reset_image_recon_preview()
        self.view.clear_cor_table()
        self.model.initial_select_data(stack)
        self.view.rotation_centre = self.model.last_cor.value
        self.do_update_projection()
        self.do_reconstruct_slice()

    def set_preview_projection_idx(self, idx):
        self.model.preview_projection_idx = idx
        self.do_update_projection()

    def set_preview_slice_idx(self, idx):
        self.model.preview_slice_idx = idx
        self.do_update_projection()
        self.do_reconstruct_slice()

    def set_row(self, row):
        self.model.selected_row = row

    def do_update_projection(self):
        images = self.model.images
        if images is not None:
            img_data = images.projection(self.model.preview_projection_idx)
            self.view.update_projection(img_data, self.model.preview_slice_idx, self.model.tilt_angle)

    def do_add_cor(self):
        row = self.model.selected_row
        cor = self.model.get_me_a_cor()
        self.view.add_cor_table_row(row, self.model.preview_slice_idx, cor.value)

    def do_reconstruct_volume(self):
        if not self.model.has_results:
            raise ValueError("Fit is not performed on the data, therefore the CoR cannot be found for each slice.")

        start_async_task_view(self.view, self.model.run_full_recon, self._on_volume_recon_done,
                              {'recon_params': self.view.recon_params()})

    def do_reconstruct_slice(self, cor=None, slice_idx=None, refresh_recon_slice_histogram=True):
        if slice_idx is None:
            slice_idx = self.model.preview_slice_idx
        else:
            self.model.preview_slice_idx = slice_idx

        # If no COR is provided and there are regression results then calculate
        # the COR for the selected preview slice
        cor = self.model.get_me_a_cor(cor)

        self.view.update_sinogram(self.model.images.sino(slice_idx))
        data = self.model.run_preview_recon(slice_idx, cor, self.view.recon_params())
        self.view.update_recon_preview(data, refresh_recon_slice_histogram)

    def _do_refine_selected_cor(self):
        slice_idx = self.model.preview_slice_idx

        dialog = CORInspectionDialogView(self.view, self.model.images, slice_idx, self.model.last_cor,
                                         self.model.proj_angles, self.view.recon_params())

        res = dialog.exec()
        LOG.debug('COR refine dialog result: {}'.format(res))
        if res == CORInspectionDialogView.Accepted:
            new_cor = dialog.optimal_rotation_centre
            LOG.debug('New optimal rotation centre: {}'.format(new_cor))
            self.model.data_model.set_cor_at_slice(slice_idx, new_cor.value)
            self.model.last_cor = new_cor
            # Update reconstruction preview with new COR
            self.do_reconstruct_slice(new_cor, slice_idx)

    def do_cor_fit(self):
        self.model.do_fit()
        self.view.set_results(*self.model.get_results())
        self.do_update_projection()
        self.do_reconstruct_slice()

    def _on_volume_recon_done(self, task):
        self.view.show_recon_volume(task.result)

    def do_clear_all_cors(self):
        self.view.clear_cor_table()
        self.model.reset_selected_row()

    def do_remove_selected_cor(self):
        self.view.remove_selected_cor()

    def set_last_cor(self, cor):
        self.model.last_cor = ScalarCoR(cor)

    def do_calculate_cors_from_manual_tilt(self):
        cor = ScalarCoR(self.view.rotation_centre)
        tilt = Degrees(self.view.tilt)
        self._set_precalculated_cor_tilt(cor, tilt)

    def _set_precalculated_cor_tilt(self, cor: ScalarCoR, tilt: Degrees):
        self.model.set_precalculated(cor, tilt)
        self.view.set_results(*self.model.get_results())
        for idx, point in enumerate(self.model.data_model.iter_points()):
            self.view.set_table_point(idx, point.slice_index, point.cor)
        self.do_update_projection()
        self.do_reconstruct_slice()

    def do_auto_find_cor(self):
        if self.model.images is None:
            return
        method = self.view.get_auto_cor_method()
        if method == AutoCorMethod.CORRELATION:
            self._auto_find_correlation()
        else:
            self._auto_find_minimisation_square_sum()

    def _auto_find_correlation(self):
        # with operation_in_progress("Finding COR using correlation...", "This may take a bit"):
        def completed(task: TaskWorkerThread):
            cor, tilt = task.result
            self._set_precalculated_cor_tilt(cor, tilt)

        start_async_task_view(self.view, self.model.auto_find_correlation, completed)

    def _auto_find_minimisation_square_sum(self):
        num_cors = self.view.get_number_of_cors()
        if num_cors is None:
            return

        self.do_clear_all_cors()

        selected_row, slice_indices = self.model.get_slice_indices(num_cors)

        if self.model.has_results:
            initial_cor = []
            for slc in slice_indices:
                initial_cor.append(self.model.data_model.get_cor_from_regression(slc))
        else:
            initial_cor = self.view.rotation_centre

        def _completed_finding_cors(task: TaskWorkerThread):
            cors = task.result
            for slice_idx, cor in zip(slice_indices, cors):
                self.view.add_cor_table_row(selected_row, slice_idx, cor)
            self.do_cor_fit()

        start_async_task_view(self.view, self.model.auto_find_minimisation_sqsum, _completed_finding_cors, {
            'slices': slice_indices,
            'recon_params': self.view.recon_params(),
            'initial_cor': initial_cor
        })
