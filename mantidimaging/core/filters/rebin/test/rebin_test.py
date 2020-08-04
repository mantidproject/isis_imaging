import unittest
from unittest import mock

import numpy as np
import numpy.testing as npt

import mantidimaging.test_helpers.unit_test_helper as th
from mantidimaging.core.filters.rebin import RebinFilter
from mantidimaging.core.utility.memory_usage import get_memory_usage_linux


class RebinTest(unittest.TestCase):
    """
    Test rebin filter.

    Tests return value only.
    """

    def __init__(self, *args, **kwargs):
        super(RebinTest, self).__init__(*args, **kwargs)

    def test_not_executed_rebin_negative(self):
        images = th.generate_images()

        mode = 'reflect'
        val = -1

        result = RebinFilter.filter_func(images, val, mode)

        npt.assert_equal(result, images)

    def test_not_executed_rebin_zero(self):
        images = th.generate_images()

        mode = 'reflect'
        val = 0

        result = RebinFilter.filter_func(images, val, mode)

        npt.assert_equal(result, images)

    def test_executed_uniform_par_2(self):
        self.do_execute_uniform(2.0)

    def test_executed_uniform_par_5(self):
        self.do_execute_uniform(5.0)

    def test_executed_uniform_seq_2(self):
        th.switch_mp_off()
        self.do_execute_uniform(2.0)
        th.switch_mp_on()

    def test_executed_uniform_seq_5(self):
        th.switch_mp_off()
        self.do_execute_uniform(5.0)
        th.switch_mp_on()

    def test_executed_uniform_seq_5_int(self):
        th.switch_mp_off()
        self.do_execute_uniform(5.0, np.int32)
        th.switch_mp_on()

    def do_execute_uniform(self, val=2.0, dtype=np.float32):
        images = th.generate_images(dtype=dtype, automatic_free=False)
        mode = 'reflect'

        expected_x = int(images.data.shape[1] * val)
        expected_y = int(images.data.shape[2] * val)

        result = RebinFilter.filter_func(images, val, mode)

        npt.assert_equal(result.data.shape[1], expected_x)
        npt.assert_equal(result.data.shape[2], expected_y)

        self.assertEqual(images.data.dtype, dtype)
        self.assertEqual(result.data.dtype, dtype)
        images.free_memory()

    def test_executed_xy_par_128_256(self):
        self.do_execute_xy((128, 256))

    def test_executed_xy_par_512_256(self):
        self.do_execute_xy((512, 256))

    def test_executed_xy_par_1024_1024(self):
        self.do_execute_xy((1024, 1024))

    def test_executed_xy_seq_128_256(self):
        th.switch_mp_off()
        self.do_execute_xy((128, 256))
        th.switch_mp_on()

    def test_executed_xy_seq_512_256(self):
        th.switch_mp_off()
        self.do_execute_xy((512, 256))
        th.switch_mp_on()

    def test_executed_xy_seq_1024_1024(self):
        th.switch_mp_off()
        self.do_execute_xy((1024, 1024))
        th.switch_mp_on()

    def do_execute_xy(self, val=(512, 512)):
        images = th.generate_images(automatic_free=False)
        mode = 'reflect'

        expected_x = int(val[0])
        expected_y = int(val[1])

        result = RebinFilter.filter_func(images, rebin_param=val, mode=mode)

        npt.assert_equal(result.data.shape[1], expected_x)
        npt.assert_equal(result.data.shape[2], expected_y)

        images.free_memory()

    def test_memory_change_acceptable(self):
        """
        This filter will increase the memory usage as it has to allocate memory
        for the new resized shape
        """
        images = th.generate_images(automatic_free=False)

        mode = 'reflect'
        # This about doubles the memory. Value found from running the test
        val = 100.

        expected_x = int(images.data.shape[1] * val)
        expected_y = int(images.data.shape[2] * val)

        cached_memory = get_memory_usage_linux(kb=True)[0]

        result = RebinFilter.filter_func(images, val, mode)

        self.assertLess(get_memory_usage_linux(kb=True)[0], cached_memory * 2)

        npt.assert_equal(result.data.shape[1], expected_x)
        npt.assert_equal(result.data.shape[2], expected_y)

        images.free_memory()

    def test_execute_wrapper_return_is_runnable(self):
        """
        Test that the partial returned by execute_wrapper can be executed (kwargs are named correctly)
        """
        rebin_to_dimensions_radio = mock.Mock()
        rebin_to_dimensions_radio.isChecked = mock.Mock(return_value=False)
        rebin_by_factor_radio = mock.Mock()
        rebin_by_factor_radio.isChecked = mock.Mock(return_value=True)
        factor = mock.Mock()
        factor.value = mock.Mock(return_value=0)
        mode_field = mock.Mock()
        mode_field.currentText = mock.Mock(return_value=0)
        execute_func = RebinFilter.execute_wrapper(rebin_to_dimensions_radio=rebin_to_dimensions_radio,
                                                   rebin_by_factor_radio=rebin_by_factor_radio,
                                                   factor=factor,
                                                   mode_field=mode_field)

        images = th.generate_images(automatic_free=False)
        execute_func(images)
        images.free_memory()

        self.assertEqual(rebin_to_dimensions_radio.isChecked.call_count, 1)
        self.assertEqual(rebin_by_factor_radio.isChecked.call_count, 1)
        self.assertEqual(factor.value.call_count, 1)
        self.assertEqual(mode_field.currentText.call_count, 1)


if __name__ == '__main__':
    unittest.main()
