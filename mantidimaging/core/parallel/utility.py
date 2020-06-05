import atexit
import ctypes
import os
import uuid
from contextlib import contextmanager
from logging import getLogger
from typing import Union, Type, Optional, Tuple

import SharedArray as sa
import numpy as np

LOG = getLogger(__name__)

SimpleCType = Union[Type[ctypes.c_uint8], Type[ctypes.c_uint16], Type[ctypes.c_int32], Type[ctypes.c_int64],
                    Type[ctypes.c_float], Type[ctypes.c_double]]


def free_all():
    for arr in sa.list():
        sa.delete(arr.name.decode("utf-8"))


atexit.register(free_all)

DTYPE_TYPES = Union[str, np.dtype, int]


def _format_name(name):
    return os.path.basename(name)


def delete_shared_array(name, silent_failure=False):
    try:
        sa.delete(f"shm://{_format_name(name)}")
    except FileNotFoundError as e:
        if not silent_failure:
            raise e


def create_array(name: Optional[str], shape: Tuple[int, int, int], dtype: DTYPE_TYPES = np.float32) -> np.ndarray:
    """

    :param name: Name of the shared memory array. If None, a non-shared array will be created
    :param shape: Shape of the array
    :param dtype: Dtype of the array
    :return: The created Numpy array
    """
    if name is not None:
        return create_shared_array(name, shape, dtype)
    else:
        # if the name provided is None, then allocate an array only visible to this process
        return np.zeros(shape, dtype)


def create_shared_array(name: Optional[str], shape: Tuple[int, int, int],
                        dtype: DTYPE_TYPES = np.float32) -> np.ndarray:
    """
    :param dtype:
    :param shape:
    :param name: Name used for the shared memory file by which this memory chunk will be identified
    """
    formatted_name = _format_name(name)
    LOG.info(f"Requested shared array with name='{formatted_name}', shape={shape}, dtype={dtype}")
    memory_file_name = f"shm://{formatted_name}"
    arr = sa.create(memory_file_name, shape, dtype)
    return arr


@contextmanager
def temp_shared_array(shape, dtype: DTYPE_TYPES = np.float32, force_name=None) -> np.ndarray:
    temp_name = str(uuid.uuid4()) if not force_name else force_name
    array = create_shared_array(temp_name, shape, dtype)
    try:
        yield array
    finally:
        delete_shared_array(temp_name)


def multiprocessing_available():
    try:
        # ignore error about unused import
        import multiprocessing  # noqa: F401
        return multiprocessing
    except ImportError:
        return False


def get_cores():
    mp = multiprocessing_available()
    # get max cores on the system as default
    if not mp:
        return 1
    else:
        return mp.cpu_count()


def generate_indices(num_images):
    """
    Generate indices for each image.

    :param num_images: The number of images.
    """
    return range(num_images)


def calculate_chunksize(cores):
    # TODO possible proper calculation of chunksize, although best performance
    # has been with 1
    return 1
