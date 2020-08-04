import unittest
from unittest import mock

import numpy as np

import mantidimaging.test_helpers.unit_test_helper as th
from mantidimaging.core.filters.outliers_isis import OutliersISISFilter


class OutliersISISTest(unittest.TestCase):
    """
    Test outliers filter.

    Tests return value only.
    """
    def __init__(self, *args, **kwargs):
        super(OutliersISISTest, self).__init__(*args, **kwargs)

    def test_executed(self):
        images = th.generate_images()

        radius = 8
        threshold = 0.1

        sample = np.copy(images.data)
        result = OutliersISISFilter.filter_func(images, threshold, radius, cores=1)

        th.assert_not_equals(result.data, sample)

    def test_execute_wrapper_return_is_runnable(self):
        """
        Test that the partial returned by execute_wrapper can be executed (kwargs are named correctly)
        """
        diff_field = mock.Mock()
        diff_field.value = mock.Mock(return_value=0)
        size_field = mock.Mock()
        size_field.value = mock.Mock(return_value=0)
        axis_field = mock.Mock()
        axis_field.value = mock.Mock(return_value=0)
        execute_func = OutliersISISFilter.execute_wrapper(diff_field, size_field, axis_field)

        images = th.generate_images()
        execute_func(images)

        self.assertEqual(diff_field.value.call_count, 1)
        self.assertEqual(size_field.value.call_count, 1)
        self.assertEqual(axis_field.value.call_count, 1)


if __name__ == '__main__':
    unittest.main()
