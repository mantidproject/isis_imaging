from functools import partial

from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox
from sarepy.prep.stripe_removal_original import remove_unresponsive_and_fluctuating_stripe

from mantidimaging.core.operations.base_filter import BaseFilter, FilterGroup
from mantidimaging.core.parallel import shared_mem as psm
from mantidimaging.gui.utility.qt_helpers import Type


class RemoveDeadStripesFilter(BaseFilter):
    """Algorithm 6 in the paper. Remove unresponsive or fluctuating stripes by:
    locating stripes, correcting by interpolation. Angular direction is along
    the axis 0.

    Source: https://github.com/nghia-vo/sarepy

    Intended to be used on: Sinograms
    When: If stripes artifacts are present that have not been
    removed with outliers + flat-fielding the projections

    Caution: Horizontal stripes are caused by changes in image intensity (pixel values),
    and should be fixed by ROI Normalisation instead!
    """
    filter_name = "Remove dead stripes"

    @staticmethod
    def filter_func(images, snr=3, size=61, cores=None, chunksize=None, progress=None):
        f = psm.create_partial(remove_unresponsive_and_fluctuating_stripe, psm.return_fwd_func, snr=snr, size=size)
        psm.execute(images.data, f, cores, chunksize, progress)
        return images

    @staticmethod
    def register_gui(form, on_change, view):
        from mantidimaging.gui.utility import add_property_to_form

        label, _ = add_property_to_form("This filter requires sinograms\nto produce a sensible result.",
                                        Type.LABEL,
                                        form=form,
                                        on_change=on_change)
        # defaults taken from TomoPy integration
        # https://tomopy.readthedocs.io/en/latest/api/tomopy.prep.stripe.html#tomopy.prep.stripe.remove_all_stripe
        _, snr = add_property_to_form('Stripe ratio',
                                      Type.FLOAT,
                                      default_value=3,
                                      form=form,
                                      on_change=on_change,
                                      tooltip="Ratio used to segment between useful information and noise"
                                      ". Greater is less sensitive.")

        _, size = add_property_to_form('Stripe kernel',
                                       Type.INT,
                                       default_value=21,
                                       valid_values=(1, 100),
                                       form=form,
                                       on_change=on_change,
                                       tooltip="Window size of the median filter to remove large stripes.")

        return {'snr': snr, 'size': size}

    @staticmethod
    def execute_wrapper(snr: QDoubleSpinBox, size: QSpinBox):  # type: ignore
        return partial(RemoveDeadStripesFilter.filter_func, snr=snr.value(), size=size.value())

    @staticmethod
    def group_name() -> FilterGroup:
        return FilterGroup.Advanced
