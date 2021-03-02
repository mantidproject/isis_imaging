# Copyright (C) 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later

import operator
from functools import partial
from typing import Callable, Dict, Any

import numpy as np
import scipy.ndimage as scipy_ndimage
from PyQt5.QtWidgets import QFormLayout

from mantidimaging.core.data import Images
from mantidimaging.core.gpu import utility as gpu
from mantidimaging.core.operations.base_filter import BaseFilter, FilterGroup
from mantidimaging.core.parallel import shared as ps
from mantidimaging.core.utility.progress_reporting import Progress
from mantidimaging.gui.utility import add_property_to_form
from mantidimaging.gui.utility.qt_helpers import Type

OUTLIERS_DARK = 'dark'
OUTLIERS_BRIGHT = 'bright'
_default_radius = 3
_default_mode = OUTLIERS_BRIGHT
DIM_2D = "2D"
DIM_1D = "1D"


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
                    progress: Progress = None,
                    force_cpu=True) -> Images:
        """
        :param images: Input data
        :param diff: Pixel value difference above which to crop bright pixels
        :param radius: Size of the median filter to apply
        :param mode: Whether to remove bright or dark outliers
                    One of [OUTLIERS_BRIGHT, OUTLIERS_DARK]
        :param cores: The number of cores that will be used to process the data.
        :param progress: The progress object.
        :param force_cpu: Force execution on CPU rather than GPU.

        :return: The processed Images object
        """
        if diff and radius and diff > 0 and radius > 0:
            if force_cpu or not gpu.gpu_available():
                func = ps.create_partial(OutliersFilter._execute,
                                         ps.return_to_self,
                                         diff=diff,
                                         radius=radius,
                                         mode=mode)
                ps.shared_list = [images.data]
                ps.execute(func,
                           images.num_projections,
                           progress=progress,
                           msg=f"Outliers with threshold {diff} and kernel {radius}")
            else:
                data = OutliersFilter._execute_gpu(images, diff, radius, mode, progress)
                images.data = data
        return images

    @staticmethod
    def register_gui(form: 'QFormLayout', on_change: Callable, view) -> Dict[str, Any]:
        _, diff_field = add_property_to_form('Difference',
                                             'float',
                                             1000,
                                             valid_values=(0, 1000000),
                                             form=form,
                                             on_change=on_change,
                                             tooltip="Difference between pixels that will be used to spot outliers.\n"
                                             "It is calculated by subtracting the original image "
                                             "from the median filtered image")
        diff_field.setDecimals(7)

        _, size_field = add_property_to_form('Median kernel',
                                             Type.INT,
                                             3, (0, 1000),
                                             form=form,
                                             on_change=on_change,
                                             tooltip="The size of the median filter kernel used to find outliers.")

        _, mode_field = add_property_to_form('Mode',
                                             Type.CHOICE,
                                             valid_values=modes(),
                                             form=form,
                                             on_change=on_change,
                                             tooltip="Whether to remove bright or dark outliers")

        _, gpu_field = add_property_to_form('Use GPU',
                                            Type.BOOL,
                                            default_value=False,
                                            tooltip='Run the remove outliers filter on the GPU',
                                            form=form,
                                            on_change=on_change)

        return {'diff_field': diff_field, 'size_field': size_field, 'mode_field': mode_field, 'gpu_field': gpu_field}

    @staticmethod
    def execute_wrapper(diff_field=None, size_field=None, mode_field=None, gpu_field=None):
        return partial(OutliersFilter.filter_func,
                       diff=diff_field.value(),
                       radius=size_field.value(),
                       mode=mode_field.currentText(),
                       force_cpu=not gpu_field.isChecked())

    @staticmethod
    def group_name() -> FilterGroup:
        return FilterGroup.Basic

    @staticmethod
    def _execute_gpu(images: Images, diff, radius, mode, progress):
        data = images.data
        progress = Progress.ensure_instance(progress, num_steps=data.shape[0], task_name="Remove outlier GPU")
        cuda = gpu.CudaExecuter(data.dtype)

        with progress:
            progress.update(msg="Applying GPU outliers with threshold: {0} and " "radius {1}".format(diff, radius))
            data[:] = cuda.remove_outlier(data, diff, radius, mode, progress)

        return data


def modes():
    return [OUTLIERS_BRIGHT, OUTLIERS_DARK]
