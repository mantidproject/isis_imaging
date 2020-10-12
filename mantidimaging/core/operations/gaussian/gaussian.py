from functools import partial
from logging import getLogger

import scipy.ndimage as scipy_ndimage

from mantidimaging import helper as h
from mantidimaging.core.data import Images
from mantidimaging.core.operations.base_filter import BaseFilter
from mantidimaging.core.parallel import shared_mem as psm
from mantidimaging.core.utility.progress_reporting import Progress
from mantidimaging.gui.utility import add_property_to_form
from mantidimaging.gui.utility.qt_helpers import Type


class GaussianFilter(BaseFilter):
    """Applies Gaussian filter to the data.

    Intended to be used on: Projections

    When: As a pre-processing step to reduce noise.
    """
    filter_name = "Gaussian"

    @staticmethod
    def filter_func(data: Images, size=None, mode=None, order=None, cores=None, chunksize=None, progress=None):
        """
        :param data: Input data as a 3D numpy.ndarray
        :param size: Size of the kernel
        :param mode: The mode with which to handle the endges.
                     One of [reflect, constant, nearest, mirror, wrap].
        :param order: The order of the filter along each axis is given as a
                      sequence of integers, or as a single number.
                      An order of 0 corresponds to convolution with a Gaussian
                      kernel.
                      An order of 1, 2, or 3 corresponds to convolution
                      with the first, second or third derivatives of a Gaussian.
                      Higher order derivatives are not implemented
        :param cores: The number of cores that will be used to process the data.
        :param chunksize: The number of chunks that each worker will receive.

        :return: The processed 3D numpy.ndarray
        """
        h.check_data_stack(data)

        if size and size > 1:
            _execute(data.data, size, mode, order, cores, chunksize, progress)
        h.check_data_stack(data)
        return data

    @staticmethod
    def register_gui(form, on_change, view):
        _, size_field = add_property_to_form('Sigma', Type.INT, 3, (0, 1000), form=form, on_change=on_change,
                                             tooltip="Standard deviation for Gaussian kernel")

        _, order_field = add_property_to_form('Order', Type.INT, 0, (0, 3), form=form, on_change=on_change,
                                              tooltip="The order of the filter along each axis is given as a single number")

        _, mode_field = add_property_to_form('Edge Mode', Type.CHOICE, valid_values=modes(), form=form,
                                             on_change=on_change, tooltip="How to handle the edges of the image")

        return {'size_field': size_field, 'order_field': order_field, 'mode_field': mode_field}

    @staticmethod
    def execute_wrapper(size_field=None, order_field=None, mode_field=None):
        return partial(GaussianFilter.filter_func,
                       size=size_field.value(),
                       mode=mode_field.currentText(),
                       order=order_field.value())


def modes():
    return ['reflect', 'constant', 'nearest', 'mirror', 'wrap']


def _execute(data, size, mode, order, cores=None, chunksize=None, progress=None):
    log = getLogger(__name__)
    progress = Progress.ensure_instance(progress, task_name='Gaussian filter')

    # Parallel CPU version of the Gaussian filter
    # create the partial function to forward the parameters
    f = psm.create_partial(scipy_ndimage.gaussian_filter,
                           fwd_func=psm.return_fwd_func,
                           sigma=size,
                           mode=mode,
                           order=order)

    log.info("Starting PARALLEL gaussian filter, with pixel data type: {0}, "
             "filter size/width: {1}.".format(data.dtype, size))

    progress.update()
    data = psm.execute(data, f, cores, chunksize, progress, msg="Gaussian filter")

    progress.mark_complete()
    log.info("Finished  gaussian filter, with pixel data type: {0}, "
             "filter size/width: {1}.".format(data.dtype, size))
