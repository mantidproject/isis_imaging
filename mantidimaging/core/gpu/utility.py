# Copyright (C) 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later

import os
import numpy as np

from logging import getLogger

CUPY_NOT_IMPORTED = False

try:
    import cupy as cp
    mempool = cp.get_default_memory_pool()
except ModuleNotFoundError:
    CUPY_NOT_IMPORTED = True

MAX_CUPY_MEMORY_FRACTION = 0.8
MAX_GPU_SLICES = 100
KERNEL_FILENAME = "cuda_image_filters.cu"

EQUIVALENT_MEDIAN_PAD_MODE = {
    "reflect": "symmetric",
    "constant": "constant",
    "nearest": "edge",
    "mirror": "reflect",
    "wrap": "wrap",
}

OUTLIER_PADDING_MODE = "symmetric"

DIFF_CONVERSION = {
    np.dtype('float32'): np.single,
    np.dtype('float64'): np.double,
}


def _cupy_on_system():
    """
    :return: True if cupy is installed on the system, False otherwise.
    """
    return not CUPY_NOT_IMPORTED


def _cupy_installed_correctly():
    """
    :return: True if cupy is able to run on the system, False otherwise.
    """
    try:
        # Check that cupy was installed properly. If it is properly installed, then basic array multiplication will
        # work without getting an exception.
        a = cp.array([1])
        b = cp.array([1])
        cp.add(a, b)

        # Initialise the memory pool if the above works
        with cp.cuda.Device(0):
            mempool.set_limit(fraction=MAX_CUPY_MEMORY_FRACTION)

        # Delete arrays. Cupy should then clear the space.
        del a
        del b

        return True

    except cp.cuda.compiler.CompileException:
        return False


def gpu_available():
    """
    :return: True if cupy is installed AND working, False otherwise.
    """
    return _cupy_on_system() and _cupy_installed_correctly()


def _load_cuda_kernel(dtype):
    """
    Loads the CUDA kernel so that cupy can act as a mediator. Replaces instances of 'float' with 'double' if the dtype
    is float64.
    :param dtype: The data type of the array that is going to be processed.
    :return: The CUDA kernel in string format.
    """
    cuda_kernel = ""
    with open(os.path.join(os.path.dirname(__file__), KERNEL_FILENAME), "r") as f:
        cuda_kernel += f.read()
    if "float64" in str(dtype):
        return cuda_kernel.replace("float", "double")
    return cuda_kernel


def _free_memory_pool(arrays=[]):
    """
    Delete any given GPU arrays and instruct the memory pool to free unused blocks.
    """
    if arrays:
        arrays.clear()
    mempool.free_all_blocks()


def _create_pinned_memory(cpu_array):
    """
    Use pinned memory in order to store a numpy array on the GPU.
    :param cpu_array: The numpy array to be transferred to the GPU.
    :return: src
    """
    mem = cp.cuda.alloc_pinned_memory(cpu_array.nbytes)
    src = np.frombuffer(mem, cpu_array.dtype, cpu_array.size).reshape(cpu_array.shape)
    src[...] = cpu_array
    return src


def _send_single_array_to_gpu(cpu_array, stream):
    """
    Sends a single array to the GPU using pinned memory and a stream.
    :param cpu_array: The numpy array to be transferred to the GPU.
    :param stream: The stream used to mediate the transfer.
    :return: A GPU array.
    """
    pinned_memory = _create_pinned_memory(cpu_array.copy())
    gpu_array = cp.empty(pinned_memory.shape, dtype=cpu_array.dtype)
    gpu_array.set(pinned_memory, stream=stream)
    return gpu_array


def _send_arrays_to_gpu_with_pinned_memory(cpu_arrays, streams):
    """
    Transfer the arrays to the GPU using pinned memory. Raises an error if the GPU runs out of memory.
    :param cpu_arrays: A list of numpy arrays to be transferred to the GPU.
    :param streams: A list of streams used to mediate the transfers. Needs to have the same length as the cpu_arrays
                    list.
    :return: A list of GPU arrays.
    """
    gpu_arrays = []

    try:

        for i in range(len(cpu_arrays)):
            gpu_arrays.append(_send_single_array_to_gpu(cpu_arrays[i], streams[i]))
            # Synchronise to ensure that the upload has completed
            streams[i].synchronize()

        return gpu_arrays

    except cp.cuda.memory.OutOfMemoryError:
        getLogger(__name__).error("Unable to send arrays to GPU. Image filter not performed.")
        _free_memory_pool(gpu_arrays)
        return []


def _create_block_and_grid_args(data):
    """
    Create the block and grid arguments that are passed to the cupy. These determine how the array
    is broken up.
    :param data: The array that will be processed using the GPU.
    :return: block_size and grid_size that are passed to the CUDA kernel.
    """
    N = 10
    block_size = tuple(N for _ in range(data.ndim))
    grid_size = tuple((shape // N) + 1 if shape % N != 0 else (shape // N) for shape in data.shape)
    return block_size, grid_size


def _create_padded_array(data, filter_size, padding_mode):
    """
    Creates the padded array on the CPU for the median filter.
    :param data: The data array to be padded.
    :param filter_size: The size of the filter that will be applied to the data array.
    :param padding_mode: The desired mode for the padding.
    :return: An padded version of the data array.
    """
    pad_size = _get_padding_value(filter_size)
    return np.pad(data, pad_width=((pad_size, pad_size), (pad_size, pad_size)), mode=padding_mode)


def _replace_gpu_array_contents(gpu_array, cpu_array, stream):
    """
    Overwrites the contents of an existing GPU array with a given CPU array.
    :param gpu_array: The GPU array to be overwritten.
    :param cpu_array: The CPU array that should be used to overwrite the GPU array.
    :param stream: The stream to mediate the transfer.
    """
    gpu_array.set(cpu_array, stream)


def _get_padding_value(filter_size):
    """
    Determine the padding value by using the filter size.
    :param filter_size: The filter size.
    :return: The size of padding needed for the padded array.
    """
    return filter_size // 2


def _get_slice_limit(n_images):
    """
    Determine the number of array slices that will be sent to the GPU. If the number of images in the stack is smaller
    than MAX_GPU_SLICES than the size of the stack is used, otherwise MAX_GPU_SLICES is used.
    :param n_images: The number of images in the input data.
    :return: The maximum number of images that will be on the GPU at any one time.
    """
    if n_images > MAX_GPU_SLICES:
        return MAX_GPU_SLICES
    return n_images


def _create_padded_image_stack(data, filter_size, padding_mode):
    """
    Creates an array of padded 2D images for use with the median and remove outlier filters.
    :param data: The input data.
    :param filter_size: The size of the filter. Used to determine the size of padding needed.
    :param padding_mode: The mode argument that is passed to numpy's pad method.
    :return: A list of padded 2D images.
    """
    return [_create_padded_array(data_slice, filter_size, padding_mode) for data_slice in data]


def _create_stream_list(n_streams):
    """
    Creates a list of non-blocking CUDA streams.
    :param n_streams: The number of streams needed for the operation.
    :return: A list of n_streams many non-blokcing CUDA streams.
    """
    return [cp.cuda.Stream(non_blocking=True) for _ in range(n_streams)]


def _convert_diff(diff, dtype):
    """
    Converts the remove outlier diff value from a Python value to a numpy float/double. This is needed for the CUDA
    kernel input when passing float arguments (as opposed to arrays of floats) to the GPU.
    :return: The numpy equivalent of the float with the appropriate precision.
    """
    return DIFF_CONVERSION[dtype](diff)


class CudaExecuter:
    def __init__(self, dtype):
        import cupy as cp

        # Load the CUDA kernel through cupy
        loaded_from_source = _load_cuda_kernel(dtype)
        imaging_filter_module = cp.RawModule(code=loaded_from_source)
        self.single_image_median_filter = imaging_filter_module.get_function("two_dimensional_median_filter")
        self.single_image_remove_bright_outlier_filter = imaging_filter_module.get_function(
            "two_dimensional_remove_bright_outliers")
        self.single_image_remove_dark_outlier_filter = imaging_filter_module.get_function(
            "two_dimensional_remove_dark_outliers")

        # Warm up the CUDA functions
        self._warm_up(dtype)

    def _warm_up(self, dtype):
        """
        Runs the median and remove outlier filters on a small test array in order to allow it to compile then deletes
        the GPU arrays.
        :param dtype: The data type of the input array.
        """
        filter_size = 3
        test_array_size = 10
        padded_array_size = test_array_size + _get_padding_value(filter_size)

        test_data = cp.random.uniform(low=0, high=5, size=(test_array_size, test_array_size)).astype(dtype)
        test_padding = cp.random.uniform(low=0, high=5, size=(padded_array_size, padded_array_size)).astype(dtype)
        block_size, grid_size = _create_block_and_grid_args(test_data[0])
        self._cuda_single_image_median_filter(test_data, test_padding, filter_size, grid_size, block_size)

        diff = 0.5
        self._cuda_single_image_remove_bright_outlier(test_data, test_padding, filter_size, diff, grid_size, block_size)
        self._cuda_single_image_remove_dark_outlier(test_data, test_padding, filter_size, diff, grid_size, block_size)

        # Clear the test arrays
        _free_memory_pool([test_data, test_padding])

    def _cuda_single_image_median_filter(self, input_data, padded_data, filter_size, grid_size, block_size):
        """
        Run the median filter on a single 2D image using CUDA.
        :param input_data: A 2D GPU data array.
        :param padded_data: The corresponding padded GPU array.
        :param filter_size: The size of the filter.
        :param grid_size: The grid size for carrying out the CUDa operation.
        :param block_size: The block size for carrying out the CUDA operation.
        """
        self.single_image_median_filter(
            grid_size,
            block_size,
            (
                input_data,
                padded_data,
                input_data.shape[0],
                input_data.shape[1],
                filter_size,
            ),
        )

    def _cuda_single_image_remove_bright_outlier(self, input_data, padded_data, filter_size, diff, grid_size,
                                                 block_size):
        """
        Run the remove bright outlier filter on a single 2D image using CUDA.
        :param input_data: A 2D GPU data array.
        :param padded_data: The corresponding padded GPU array.
        :param filter_size: The size of the filter.
        :param diff: The diff threshold for replacing the pixel value with its neighbour median.
        :param grid_size: The grid size for carrying out the CUDa operation.
        :param block_size: The block size for carrying out the CUDA operation.
        """
        self.single_image_remove_bright_outlier_filter(grid_size, block_size, (
            input_data,
            padded_data,
            input_data.shape[0],
            input_data.shape[1],
            filter_size,
            _convert_diff(diff, input_data.dtype),
        ))

    def _cuda_single_image_remove_dark_outlier(self, input_data, padded_data, filter_size, diff, grid_size, block_size):
        """
        Run the remove dark outlier filter on a single 2D image using CUDA.
        :param input_data: A 2D GPU data array.
        :param padded_data: The corresponding padded GPU array.
        :param filter_size: The size of the filter.
        :param diff: The diff threshold for replacing the pixel value with its neighbour median.
        :param grid_size: The grid size for carrying out the CUDa operation.
        :param block_size: The block size for carrying out the CUDA operation.
        """
        self.single_image_remove_dark_outlier_filter(grid_size, block_size, (
            input_data,
            padded_data,
            input_data.shape[0],
            input_data.shape[1],
            filter_size,
            _convert_diff(diff, input_data.dtype),
        ))

    def median_filter(self, data, filter_size, mode, progress):
        """
        Runs the median filter on a stack of 2D images asynchronously.

        The data array with the median filter applied to it provided the GPU didn't run out of space,
        otherwise it returns the unaltered input array.

        :param data: The CPU data array containing a stack of 2D images.
        :param filter_size: The filter size.
        :param mode: The mode for the filter. Determines how the edge values are managed.
        :param progress: An object for displaying the filter progress.
        :return: Data with median filter applied on success, else unaltered input array
        """

        # Try to free memory
        _free_memory_pool()

        n_images = data.shape[0]

        # Set the maximum number of images that will be on the GPU at a time
        slice_limit = _get_slice_limit(n_images)

        cpu_padded_images = _create_padded_image_stack(data, filter_size, EQUIVALENT_MEDIAN_PAD_MODE[mode])

        streams = _create_stream_list(slice_limit)

        # Send the data arrays and padded arrays to the GPU in slices
        gpu_data_slices = _send_arrays_to_gpu_with_pinned_memory(data[:slice_limit], streams)
        gpu_padded_data = _send_arrays_to_gpu_with_pinned_memory(cpu_padded_images[:slice_limit], streams)

        # Return if the data transfer was not successful
        if not gpu_data_slices or not gpu_padded_data:
            return data

        block_size, grid_size = _create_block_and_grid_args(gpu_data_slices[0])

        for i in range(n_images):

            # Use the current stream
            streams[i % slice_limit].use()

            # Overwrite the contents of the GPU arrays
            if i >= slice_limit:
                _replace_gpu_array_contents(gpu_data_slices[i % slice_limit], data[i], streams[i % slice_limit])
                _replace_gpu_array_contents(
                    gpu_padded_data[i % slice_limit],
                    cpu_padded_images[i],
                    streams[i % slice_limit],
                )

            # Synchronise the current stream to ensure that the overwriting is complete
            streams[i % slice_limit].synchronize()

            # Apply the median filter on the individual image
            self._cuda_single_image_median_filter(gpu_data_slices[i % slice_limit], gpu_padded_data[i % slice_limit],
                                                  filter_size, grid_size, block_size)

            # Synchronise to ensure that the GPU median filter has completed
            streams[i % slice_limit].synchronize()

            # Transfer the GPU result to a CPU array
            data[i][:] = gpu_data_slices[i % slice_limit].get(streams[i % slice_limit])

            progress.update()

        progress.mark_complete()

        # Free memory once the operation is complete
        _free_memory_pool(gpu_data_slices + gpu_padded_data)

        return data

    def remove_outlier(self, data, diff, filter_size, mode, progress):
        """
        Runs the remove outlier filter on a stack of 2D images asynchronously.
        :param data: The CPU data array containing a stack of 2D images.
        :param diff: The diff threshold for replacing the pixel value with its neighbour median.
        :param filter_size: The filter size.
        :param mode: The mode for the filter. Determines if bright or dark outliers are removed.
        :param progress: An object for displaying the filter progress.
        :return: The data array with the remove outlier filter applied to it provided the GPU didn't run out of space,
                 otherwise it returns the unaltered input array.
        """

        # Try to free memory
        _free_memory_pool()

        n_images = data.shape[0]

        # Set the maximum number of images that will be on the GPU at a time
        slice_limit = _get_slice_limit(n_images)

        cpu_padded_images = _create_padded_image_stack(data, filter_size, OUTLIER_PADDING_MODE)

        streams = _create_stream_list(slice_limit)

        # Send the data arrays and padded arrays to the GPU in slices
        gpu_data_slices = _send_arrays_to_gpu_with_pinned_memory(data[:slice_limit], streams)
        gpu_padded_data = _send_arrays_to_gpu_with_pinned_memory(cpu_padded_images[:slice_limit], streams)

        # Return if the data transfer was not successful
        if not gpu_data_slices or not gpu_padded_data:
            return data

        block_size, grid_size = _create_block_and_grid_args(gpu_data_slices[0])

        if mode == "bright":
            cuda_single_image_remove_outlier_filter = self._cuda_single_image_remove_bright_outlier
        else:
            cuda_single_image_remove_outlier_filter = self._cuda_single_image_remove_dark_outlier

        for i in range(n_images):

            # Use the current stream
            streams[i % slice_limit].use()

            # Overwrite the contents of the GPU arrays
            if i >= slice_limit:
                _replace_gpu_array_contents(gpu_data_slices[i % slice_limit], data[i], streams[i % slice_limit])
                _replace_gpu_array_contents(
                    gpu_padded_data[i % slice_limit],
                    cpu_padded_images[i],
                    streams[i % slice_limit],
                )

            # Synchronise the current stream to ensure that the overwriting is complete
            streams[i % slice_limit].synchronize()

            # Apply the median filter on the individual image
            cuda_single_image_remove_outlier_filter(gpu_data_slices[i % slice_limit], gpu_padded_data[i % slice_limit],
                                                    filter_size, diff, grid_size, block_size)

            # Synchronise to ensure that the GPU remove outlier filter has completed
            streams[i % slice_limit].synchronize()

            # Transfer the GPU result to a CPU array
            data[i][:] = gpu_data_slices[i % slice_limit].get(streams[i % slice_limit])

            progress.update()

        progress.mark_complete()

        # Free memory once the operation is complete
        _free_memory_pool(gpu_data_slices + gpu_padded_data)

        return data
