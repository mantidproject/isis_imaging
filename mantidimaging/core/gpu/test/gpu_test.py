import unittest

import numpy.testing as npt

import mantidimaging.test_helpers.unit_test_helper as th
from mantidimaging.core.filters.median_filter import MedianFilter, modes
from mantidimaging.core.gpu import utility as gpu

GPU_NOT_AVAIL = not gpu.gpu_available()
GPU_SKIP_REASON = "Skip GPU tests if cupy isn't installed."
GPU_UTILITY_LOC = "mantidimaging.core.gpu.utility.gpu_available"


class GPUTest(unittest.TestCase):
    """
    Test median filter.

    Tests return value and in-place modified data.
    """
    def __init__(self, *args, **kwargs):
        super(GPUTest, self).__init__(*args, **kwargs)
        if not GPU_NOT_AVAIL:
            self.cuda = gpu.CudaExecuter("float32")

    @unittest.skipIf(GPU_NOT_AVAIL, reason=GPU_SKIP_REASON)
    def test_numpy_pad_modes_match_scipy_median_modes(self):

        size = 3
        for mode in modes():
            with self.subTest(mode=mode):

                images = th.gen_img_shared_array()

                gpu_result = MedianFilter.filter_func(images.copy(), size, mode, self.cuda)

                th.switch_mp_off()
                cpu_result = MedianFilter.filter_func(images.copy(), size, mode)
                th.switch_mp_on()

                npt.assert_almost_equal(gpu_result[0], cpu_result[0])

    @unittest.skipIf(GPU_NOT_AVAIL, reason=GPU_SKIP_REASON)
    def test_gpu_result_matches_cpu_result_for_different_filter_sizes(self):

        mode = "reflect"
        for size in [5, 7, 9]:
            with self.subTest(size=size):

                images = th.gen_img_shared_array()

                gpu_result = MedianFilter.filter_func(images.copy(), size, mode, self.cuda)

                th.switch_mp_off()
                cpu_result = MedianFilter.filter_func(images.copy(), size, mode)
                th.switch_mp_on()

                npt.assert_almost_equal(gpu_result, cpu_result)

    @unittest.skipIf(GPU_NOT_AVAIL, reason=GPU_SKIP_REASON)
    def test_gpu_result_matches_cpu_result_for_larger_images(self):

        N = 1500
        size = 3
        mode = "reflect"

        images = th.gen_img_shared_array(shape=(500, N, N))

        gpu_result = MedianFilter.filter_func(images.copy(), size, mode, self.cuda)

        th.switch_mp_off()
        cpu_result = MedianFilter.filter_func(images.copy(), size, mode)
        th.switch_mp_on()

        npt.assert_almost_equal(gpu_result, cpu_result)


if __name__ == "__main__":
    unittest.main()
