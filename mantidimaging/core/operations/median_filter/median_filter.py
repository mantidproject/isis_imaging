# Copyright (C) 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later

from functools import partial
from logging import getLogger
from typing import Callable, Dict, Any, TYPE_CHECKING

import scipy.ndimage as scipy_ndimage

from mantidimaging import helper as h
from mantidimaging.core.data import Images
from mantidimaging.core.gpu import utility as gpu
from mantidimaging.core.operations.base_filter import BaseFilter
from mantidimaging.core.parallel import shared as ps
from mantidimaging.core.utility.progress_reporting import Progress
from mantidimaging.gui.utility import add_property_to_form
from mantidimaging.gui.utility.qt_helpers import Type

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QFormLayout  # pragma: no cover


class MedianFilter(BaseFilter):
    """Applies Median filter to the data.

    Intended to be used on: Projections

    When: As a pre-processing step to reduce noise.
    """
    filter_name = "Median"

    @staticmethod
    def filter_func(data: Images,
                    size=None,
                    mode="reflect",
                    cores=None,
                    chunksize=None,
                    progress=None,
                    force_cpu=True) -> Images:
        """
        :param data: Input data as an Images object.
        :param size: Size of the kernel
        :param mode: The mode with which to handle the edges.
                     One of [reflect, constant, nearest, mirror, wrap].
                     Modes are described in the `SciPy documentation
                     <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.median_filter.html>`_.
        :param cores: The number of cores that will be used to process the data.
        :param chunksize: The number of chunks that each worker will receive.
        :param progress: The object for displaying the progress.
        :param force_cpu: Whether or not to use the CPU.

        :return: Returns the processed data

        """
        h.check_data_stack(data)

        if size and size > 1:
            if not force_cpu and gpu.gpu_available():
                data = _execute_gpu(data.data, size, mode, progress)
            else:
                _execute(data.data, size, mode, cores, chunksize, progress)

        h.check_data_stack(data)
        return data

    @staticmethod
    def register_gui(form: 'QFormLayout', on_change: Callable, view) -> Dict[str, Any]:
        _, size_field = add_property_to_form('Kernel Size',
                                             Type.INT,
                                             3, (0, 1000),
                                             form=form,
                                             on_change=on_change,
                                             tooltip="Size of the median filter kernel")

        _, mode_field = add_property_to_form('Edge Mode',
                                             Type.CHOICE,
                                             valid_values=modes(),
                                             form=form,
                                             on_change=on_change,
                                             tooltip="Mode to handle the edges of the image")

        _, gpu_field = add_property_to_form('Use GPU',
                                            Type.BOOL,
                                            default_value=False,
                                            tooltip='Run the median filter on the GPU',
                                            form=form,
                                            on_change=on_change)

        return {'size_field': size_field, 'mode_field': mode_field, 'gpu_field': gpu_field}

    @staticmethod
    def execute_wrapper(size_field=None, mode_field=None, gpu_field=None):
        return partial(MedianFilter.filter_func,
                       size=size_field.value(),
                       mode=mode_field.currentText(),
                       force_cpu=not gpu_field.isChecked())


def modes():
    return ['reflect', 'constant', 'nearest', 'mirror', 'wrap']


def _execute(data, size, mode, cores=None, chunksize=None, progress=None):
    log = getLogger(__name__)
    progress = Progress.ensure_instance(progress, task_name='Median filter')

    # create the partial function to forward the parameters
    f = ps.create_partial(scipy_ndimage.median_filter, ps.return_to_self, size=size, mode=mode)

    with progress:
        log.info("PARALLEL median filter, with pixel data type: {0}, filter "
                 "size/width: {1}.".format(data.dtype, size))

        ps.shared_list = [data]
        ps.execute(f, data.shape[0], progress, msg="Median filter", cores=cores)

    return data


def _execute_gpu(data, size, mode, progress=None):
    log = getLogger(__name__)
    progress = Progress.ensure_instance(progress, num_steps=data.shape[0], task_name="Median filter GPU")
    cuda = gpu.CudaExecuter(data.dtype)

    with progress:
        log.info("GPU median filter, with pixel data type: {0}, filter " "size/width: {1}.".format(data.dtype, size))

        data = cuda.median_filter(data, size, mode, progress)

    return Images(data)
