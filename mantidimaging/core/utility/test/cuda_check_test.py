# Copyright (C) 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
import unittest
from unittest.mock import patch

from mantidimaging.core.utility import cuda_check
from mantidimaging.core.utility.cuda_check import NVIDIA_SMI, EXCEPTION_MSG, LOCATE


class TestCudaCheck(unittest.TestCase):
    @patch("mantidimaging.core.utility.cuda_check.subprocess.check_output")
    def test_cuda_is_present_returns_true(self, check_output_mock):
        check_output_mock.side_effect = [b"Driver Version", b"/usr/lib/path/to/libcuda.so\n"]
        assert cuda_check._cuda_is_present()

    @patch("mantidimaging.core.utility.cuda_check.subprocess.check_output")
    def test_cuda_is_present_returns_false(self, check_output_mock):
        nvidia_error = "NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver. Make sure that " \
                       "the latest NVIDIA driver is installed and running.\n "
        check_output_mock.side_effect = [str.encode(nvidia_error), b"/path/to/libcuda.so\n"]

        with self.assertLogs(cuda_check.__name__, level='ERROR') as cuda_check_log:
            assert not cuda_check._cuda_is_present()
        self.assertIn(nvidia_error, cuda_check_log.output[0])

    @patch("mantidimaging.core.utility.cuda_check.subprocess.check_output")
    def test_failed_libcuda_search_is_logged(self, check_output_mock):
        check_output_mock.side_effect = [b"Driver Version", b""]
        with self.assertLogs(cuda_check.__name__, level='ERROR') as cuda_check_log:
            assert not cuda_check._cuda_is_present()
        self.assertIn("Search for libcuda files returned no results.", cuda_check_log.output[0])

    @patch("mantidimaging.core.utility.cuda_check.subprocess.check_output")
    def test_cuda_is_present_returns_false_when_subprocess_raises_exception(self, check_output_mock):
        with self.assertLogs(cuda_check.__name__, level='ERROR') as cuda_check_log:
            check_output_mock.side_effect = PermissionError
            assert not cuda_check._cuda_is_present()

            check_output_mock.side_effect = FileNotFoundError
            assert not cuda_check._cuda_is_present()

        nvidia_exception_msg = f"{EXCEPTION_MSG} {NVIDIA_SMI}"
        locate_exception_msg = f"{EXCEPTION_MSG} {LOCATE}"

        self.assertIn(nvidia_exception_msg, cuda_check_log.output[0])
        self.assertIn(locate_exception_msg, cuda_check_log.output[1])
        self.assertIn(nvidia_exception_msg, cuda_check_log.output[2])
        self.assertIn(locate_exception_msg, cuda_check_log.output[3])

    def test_not_found_message(self):
        short_msg, long_msg = cuda_check.not_found_message()
        assert short_msg == "Working CUDA installation not found."
        assert long_msg == "Working CUDA installation not found. Will only use gridrec algorithm for reconstruction."