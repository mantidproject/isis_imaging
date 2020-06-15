import unittest
from typing import Tuple
from unittest import mock

import numpy as np
import numpy.testing as npt

import mantidimaging.test_helpers.unit_test_helper as th
from mantidimaging.core.data import Images
from mantidimaging.core.filters.flat_fielding import FlatFieldFilter


class FlatFieldingTest(unittest.TestCase):
    """
    Test background correction filter.

    Tests return value and in-place modified data.
    """
    def __init__(self, *args, **kwargs):
        super(FlatFieldingTest, self).__init__(*args, **kwargs)

    def _make_images(self) -> Tuple[Images, Images, Images]:
        images = th.generate_images()

        flat = th.generate_images()
        dark = th.generate_images()
        return images, flat, dark

    def test_real_result(self):
        th.switch_mp_off()
        self.do_real_result()
        th.switch_mp_on()

    def do_real_result(self):
        # the calculation here was designed on purpose to have a value
        # below the np.clip in flat_fielding
        # the operation is (sample - dark) / (flat - dark)
        images, flat, dark = self._make_images()
        images.sample[:] = 26.
        flat.sample[:] = 7.
        dark.sample[:] = 6.

        expected = np.full(images.sample.shape, 20.)

        # we dont want anything to be cropped out
        result = FlatFieldFilter.filter_func(images, flat, dark, clip_max=20)

        npt.assert_almost_equal(result.sample, expected, 7)

    def test_clip_max_works(self):
        # the calculation here was designed on purpose to have a value
        # ABOVE the np.clip in flat_fielding
        # the operation is (sample - dark) / (flat - dark)
        images, flat, dark = self._make_images()
        images.sample[:] = 846.
        flat.sample[:] = 42.
        dark.sample[:] = 6.
        expected = np.full(images.sample.shape, 3.)

        # the resulting values from the calculation are above 3,
        # but clip_max should make them all equal to 3
        result = FlatFieldFilter.filter_func(images, flat, dark, clip_max=3)

        npt.assert_equal(result.sample, expected)
        npt.assert_equal(images.sample, expected)

        npt.assert_equal(result.sample, images.sample)

    def test_clip_min_works(self):
        images, flat, dark = self._make_images()
        images.sample[:] = 846.
        flat.sample[:] = 42.
        dark.sample[:] = 6.
        expected = np.full(images.sample.shape, 300.)

        # the resulting values from above are below 300,
        # but clip min should make all values below 300, equal to 300
        result = FlatFieldFilter.filter_func(images, flat, dark, clip_min=300)

        npt.assert_equal(result.sample, expected)
        npt.assert_equal(images.sample, expected)

        npt.assert_equal(result.sample, images.sample)

    @mock.patch(f'{FlatFieldFilter.__module__ + ".get_average_image"}', mock.MagicMock(return_value=None))
    def test_execute_wrapper_return_is_runnable(self):
        """
        Test that the partial returned by execute_wrapper can be executed (kwargs are named correctly)
        """
        fake_presenter = mock.MagicMock()
        fake_presenter.presenter.images = th.generate_images()
        flat_widget = mock.Mock()
        flat_widget.main_window.get_stack_visualiser = mock.Mock()
        flat_widget.main_window.get_stack_visualiser.return_value = fake_presenter
        dark_widget = mock.Mock()
        dark_widget.main_window.get_stack_visualiser = mock.Mock()
        dark_widget.main_window.get_stack_visualiser.return_value = fake_presenter
        execute_func = FlatFieldFilter.execute_wrapper(flat_widget, dark_widget)
        images = th.generate_images()
        execute_func(images)


if __name__ == '__main__':
    unittest.main()
