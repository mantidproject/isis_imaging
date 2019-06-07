import json
from concurrent.futures import Future
from functools import partial
from logging import getLogger

import numpy as np

from mantidimaging.core.utility.registrator import (
    get_package_children,
    import_items,
    register_into
)
from mantidimaging.gui.utility import get_auto_params_from_stack
from mantidimaging.gui.windows.savu_filters import preparation
from mantidimaging.gui.windows.stack_visualiser import (
    Notification as SVNotification)


def ensure_tuple(val):
    return val if isinstance(val, tuple) else (val,)


class Panic(Exception):
    def __init__(self, message):
        message = f"EVERYTHING HAS GONE TERRIBLY WRONG.\n\n{message}"
        super(Exception, self).__init__(message)


class SavuFiltersWindowModel(object):

    def __init__(self):
        super(SavuFiltersWindowModel, self).__init__()

        # Update the local filter registry
        self.filters = None
        self.response = preparation.data.get()  # type: Future
        if not self.response.running():
            response = self.response.result()
            print(json.loads(response.content))
        else:
            raise Panic("HELP")
        self.register_filters('mantidimaging.core.filters',
                              ['mantidimaging.core.filters.wip'])

        self.preview_image_idx = 0

        # Execution info for current filter
        self.stack = None
        self.do_before = None
        self.execute = None
        self.do_after = None

    def register_filters(self, package_name, ignored_packages=None):
        """
        Builds a local registry of filters.

        Filter name is used to initially populate the combo box for filter
        selection.

        The _gui_register function is then used to setup the filter specific
        properties and the execution mode.

        :param package_name: Name of the root package in which to search for
                             filters

        :param ignored_packages: List of ignore rules
        """
        filter_packages = get_package_children(package_name, packages=True,
                                               ignore=ignored_packages)

        filter_packages = [p[1] for p in filter_packages]

        loaded_filters = import_items(filter_packages,
                                      ['execute', 'NAME', '_gui_register'])

        loaded_filters = filter(
            lambda f: f.available() if hasattr(f, 'available') else True,
            loaded_filters)

        def register_filter(filter_list, module):
            filter_list.append((module.NAME, module._gui_register))

        self.filters = []
        register_into(loaded_filters, self.filters, register_filter)

    @property
    def filter_names(self):
        return [f[0] for f in self.filters]

    def filter_registration_func(self, filter_idx):
        """
        Gets the function used to register the GUI of a given filter.

        :param filter_idx: Index of the filter in the registry
        """
        return self.filters[filter_idx][1]

    @property
    def stack_presenter(self):
        return self.stack.presenter if self.stack else None

    @property
    def num_images_in_stack(self):
        num_images = self.stack_presenter.images.sample.shape[0] \
            if self.stack_presenter is not None else 0
        return num_images

    def setup_filter(self, filter_specifics):
        """
        Sets filter properties from result of registration function.
        """
        self.auto_props, self.do_before, self.execute, self.do_after = \
            filter_specifics

    def apply_filter(self, images, exec_kwargs):
        """
        Applies the selected filter to a given image stack.
        """
        log = getLogger(__name__)

        # Generate the execute partial from filter registration
        do_before_func = self.do_before() if self.do_before else lambda _: ()
        do_after_func = self.do_after() if self.do_after else lambda *_: None
        execute_func = self.execute()

        # Log execute function parameters
        log.info("Filter kwargs: {}".format(exec_kwargs))
        if isinstance(execute_func, partial):
            log.info("Filter partial args: {}".format(execute_func.args))
            log.info("Filter partial kwargs: {}".format(execute_func.keywords))

            all_kwargs = execute_func.keywords.copy()
            all_kwargs.update(exec_kwargs)

            images.record_parameters_in_metadata(
                '{}.{}'.format(execute_func.func.__module__,
                               execute_func.func.__name__),
                *execute_func.args, **all_kwargs)

        # Do preprocessing and save result
        preproc_res = do_before_func(images.sample)
        preproc_res = ensure_tuple(preproc_res)

        # Run filter
        ret_val = execute_func(images.sample, **exec_kwargs)

        # Handle the return value from the algorithm dialog
        if isinstance(ret_val, tuple):
            # Tuples are assumed to be three elements containing sample, flat
            # and dark images
            images.sample, images.flat, images.dark = ret_val
        elif isinstance(ret_val, np.ndarray):
            # Single Numpy arrays are assumed to be just the sample image
            images.sample = ret_val
        else:
            log.debug('Unknown execute return value: {}'.format(type(ret_val)))

        # Do postprocessing using return value of preprocessing as parameter
        do_after_func(images.sample, *preproc_res)

    def do_apply_filter(self):
        """
        Applies the selected filter to the selected stack.
        """
        if not self.stack_presenter:
            raise ValueError('No stack selected')

        # Get auto parameters
        exec_kwargs = get_auto_params_from_stack(
            self.stack_presenter, self.auto_props)

        self.apply_filter(self.stack_presenter.images, exec_kwargs)

        # Refresh the image in the stack visualiser
        self.stack_presenter.notify(SVNotification.REFRESH_IMAGE)
