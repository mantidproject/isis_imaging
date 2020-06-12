import unittest
from unittest import mock

import numpy as np

import mantidimaging.test_helpers.unit_test_helper as th
from mantidimaging.core.filters.circular_mask import CircularMaskFilter
from mantidimaging.core.utility.memory_usage import get_memory_usage_linux


class CircularMaskTest(unittest.TestCase):
    """
    Test circular mask filter.

    Tests return value and in-place modified data.
    """
    def __init__(self, *args, **kwargs):
        super(CircularMaskTest, self).__init__(*args, **kwargs)

    def test_executed(self):
        images = th.generate_images_class_random_shared_array()

        ratio = 0.9

        self.assertNotEqual(images.sample[0, 0, 0], 0)
        self.assertNotEqual(images.sample[0, 0, -1], 0)

        result = CircularMaskFilter.filter_func(images, ratio)
        self.assertEqual(result.sample[0, 0, 0], 0)
        self.assertEqual(result.sample[0, 0, -1], 0)

    def test_memory_change_acceptable(self):
        """
        Expected behaviour for the filter is to be done in place
        without using more memory.

        In reality the memory is increased by about 40MB (4 April 2017),
        but this could change in the future.

        The reason why a 10% window is given on the expected size is
        to account for any library imports that may happen.

        This will still capture if the data is doubled, which is the main goal.
        """
        images = th.generate_images_class_random_shared_array()
        ratio = 0.9
        original = np.copy(images.sample)
        cached_memory = get_memory_usage_linux(kb=True)[0]

        result = CircularMaskFilter.filter_func(images, ratio)

        self.assertLess(get_memory_usage_linux(kb=True)[0], cached_memory * 1.1)

        th.assert_not_equals(result.sample, original)

    def test_execute_wrapper_return_is_runnable(self):
        """
        Test that the partial returned by execute_wrapper can be executed (kwargs are named correctly)
        """
        radius_field = mock.Mock()
        radius_field.value = mock.Mock(return_value=0)
        value_field = mock.Mock()
        value_field.value = mock.Mock(return_value=0)
        execute_func = CircularMaskFilter.execute_wrapper(radius_field, value_field)

        images = th.generate_images_class_random_shared_array()
        execute_func(images)

        self.assertEqual(radius_field.value.call_count, 1)
        self.assertEqual(value_field.value.call_count, 1)


if __name__ == '__main__':
    unittest.main()
