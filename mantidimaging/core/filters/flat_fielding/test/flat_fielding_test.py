import unittest
from unittest import mock

import numpy as np
import numpy.testing as npt

import mantidimaging.test_helpers.unit_test_helper as th
from mantidimaging.core.filters.flat_fielding import FlatFieldFilter


class BackgroundCorrectionTest(unittest.TestCase):
    """
    Test background correction filter.

    Tests return value and in-place modified data.
    """
    def __init__(self, *args, **kwargs):
        super(BackgroundCorrectionTest, self).__init__(*args, **kwargs)

    def test_not_executed_empty_params(self):
        """
        Test filter doesn't execute with no parameters
        """
        images = th.generate_images_class_random_shared_array()

        # empty params
        result = FlatFieldFilter.filter_func(images)

        npt.assert_equal(result.sample, images.sample)

    def test_not_executed_no_dark(self):
        """
        Test filter doesn't execute with no dark images provided
        """
        images = th.generate_images_class_random_shared_array()
        flat = th.gen_img_shared_array()[0]

        # no dark
        result = FlatFieldFilter.filter_func(images, flat[0])

        npt.assert_equal(result.sample, images.sample)

    def test_not_executed_no_flat(self):
        """
        Test filter doesn't execute with no flat images provided
        """
        images = th.generate_images_class_random_shared_array()
        dark = th.gen_img_shared_array()[0]

        # no flat
        result = FlatFieldFilter.filter_func(images, None, dark[0])

        npt.assert_equal(result.sample, images.sample)

    def test_not_executed_bad_flat(self):
        """
        Test filter doesn't execute when flat is incorrect type
        """
        images = th.generate_images_class_random_shared_array()
        flat = th.gen_img_shared_array()[0]
        dark = th.gen_img_shared_array()[0]

        # bad flat
        npt.assert_raises(ValueError, FlatFieldFilter.filter_func, images, flat[0], dark)

    def test_not_executed_bad_dark(self):
        """
        Test filter doesn't execute when dark is incorrect type
        """
        images = th.generate_images_class_random_shared_array()
        flat = th.gen_img_shared_array()[0]
        dark = th.gen_img_shared_array()[0]

        # bad dark
        npt.assert_raises(ValueError, FlatFieldFilter.filter_func, images, flat, dark[0])

    def test_real_result(self):
        th.switch_mp_off()
        self.do_real_result()
        th.switch_mp_on()

    def do_real_result(self):
        # the calculation here was designed on purpose to have a value
        # below the np.clip in flat_fielding
        # the operation is (sample - dark) / (flat - dark)
        images = th.generate_images_class_random_shared_array()
        images.sample[:] = 26.
        flat = th.gen_img_shared_array_with_val(7., shape=(1, images.sample.shape[1], images.sample.shape[2]))[0]
        dark = th.gen_img_shared_array_with_val(6., shape=(1, images.sample.shape[1], images.sample.shape[2]))[0]

        expected = np.full(images.sample.shape, 20.)

        # we dont want anything to be cropped out
        result = FlatFieldFilter.filter_func(images, flat, dark, clip_max=20)

        npt.assert_almost_equal(result.sample, expected, 7)

    def test_clip_max_works(self):
        # the calculation here was designed on purpose to have a value
        # ABOVE the np.clip in flat_fielding
        # the operation is (sample - dark) / (flat - dark)
        images = th.generate_images_class_random_shared_array()
        images.sample[:] = 846.
        flat = th.gen_img_shared_array()[0]
        flat[:] = 42.
        dark = th.gen_img_shared_array()[0]
        dark[:] = 6.
        expected = np.full(images.sample.shape, 3.)

        # the resulting values from the calculation are above 3,
        # but clip_max should make them all equal to 3
        result = FlatFieldFilter.filter_func(images, flat, dark, clip_max=3)

        npt.assert_equal(result.sample, expected)
        npt.assert_equal(images.sample, expected)

        npt.assert_equal(result.sample, images.sample)

    def test_clip_min_works(self):
        images = th.generate_images_class_random_shared_array()
        images.sample[:] = 846.
        flat = th.gen_img_shared_array()[0]
        flat[:] = 42.
        dark = th.gen_img_shared_array()[0]
        dark[:] = 6.
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
        execute_func = FlatFieldFilter.execute_wrapper(flat_widget=None, dark_widget=None)
        images = th.generate_images_class_random_shared_array()
        execute_func(images)


if __name__ == '__main__':
    unittest.main()