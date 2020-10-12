import operator
from functools import partial

import numpy as np
import scipy.ndimage as scipy_ndimage

from mantidimaging.core.data import Images
from mantidimaging.core.operations.base_filter import BaseFilter
from mantidimaging.core.parallel import utility as pu, shared as ps
from mantidimaging.core.utility.progress_reporting import Progress
from mantidimaging.gui.utility import add_property_to_form
from mantidimaging.gui.utility.qt_helpers import Type

OUTLIERS_DARK = 'dark'
OUTLIERS_BRIGHT = 'bright'
_default_radius = 3
_default_mode = OUTLIERS_BRIGHT
DIM_2D = "2D"
DIM_1D = "1D"
_default_dim = DIM_2D


class OutliersFilter(BaseFilter):
    """Removes pixel values that are found to be outliers by the parameters.

    Intended to be used on: Projections

    When: As a pre-processing step to reduce very bright or dead pixels in the data.

    Caution: This should usually be the first step applied to the data, flat and dark
    images, to remove pixels with very large values that will cause issues in the flat-fielding.
    """
    filter_name = "Remove Outliers"

    @staticmethod
    def _execute(data, diff, radius, mode):
        # Adapted from tomopy source
        median = scipy_ndimage.median_filter(data, radius)
        if mode == OUTLIERS_BRIGHT:
            op = operator.ge
        else:
            op = operator.le
        return np.where(op(data - median, diff), median, data)

    @staticmethod
    def filter_func(images: Images,
                    diff=None,
                    radius=_default_radius,
                    mode=_default_mode,
                    cores=None,
                    progress: Progress = None):
        """
        :param images: Input data
        :param diff: Pixel value difference above which to crop bright pixels
        :param radius: Size of the median filter to apply
        :param cores: The number of cores that will be used to process the data.

        :return: The processed 3D numpy.ndarray
        """
        if not pu.multiprocessing_necessary(images.data.shape, cores):
            cores = 1

        if diff and radius and diff > 0 and radius > 0:
            func = ps.create_partial(OutliersFilter._execute, ps.return_to_self1, diff=diff, radius=radius, mode=mode)
            ps.shared_list = [images.data]
            ps.execute(func,
                       images.num_projections,
                       progress=progress,
                       msg=f"Outliers with threshold {diff} and kernel {radius}",
                       cores=cores)
        return images

    @staticmethod
    def register_gui(form, on_change, view):
        _, diff_field = add_property_to_form('Difference',
                                             'float',
                                             1,
                                             valid_values=(-1000000, 1000000),
                                             form=form,
                                             on_change=on_change)
        diff_field.setDecimals(7)

        _, size_field = add_property_to_form('Median kernel',
                                             Type.INT,
                                             3, (0, 1000),
                                             form=form,
                                             on_change=on_change,
                                             tooltip="The size of the median filter kernel used to find outliers.")

        _, mode_field = add_property_to_form('Mode', Type.CHOICE, valid_values=modes(), form=form, on_change=on_change)

        return {'diff_field': diff_field, 'size_field': size_field, 'mode_field': mode_field}

    @staticmethod
    def execute_wrapper(diff_field=None, size_field=None, mode_field=None):

        return partial(OutliersFilter.filter_func,
                       diff=diff_field.value(),
                       radius=size_field.value(),
                       mode=mode_field.currentText())


def modes():
    return [OUTLIERS_BRIGHT, OUTLIERS_DARK]
