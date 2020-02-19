"""
This module handles the loading of FIT, FITS, TIF, TIFF
"""
from typing import List, Tuple, Union

import numpy as np

from mantidimaging.core.data import Images
from mantidimaging.core.io.utility import get_file_names
from mantidimaging.core.parallel import two_shared_mem as ptsm
from mantidimaging.core.parallel import utility as pu
from mantidimaging.core.utility.progress_reporting import Progress

from . import stack_loader


def execute(load_func,
            all_input_filenames,
            input_path_flat,
            input_path_dark,
            img_format,
            data_dtype,
            cores,
            chunksize,
            parallel_load,
            indices,
            construct_sinograms,
            progress=None):
    """
    Reads a stack of images into memory, assuming dark and flat images
    are in separate directories.

    If several files are found in the same directory (for example you
    give image0001.fits and there's also image0002.fits,
    image0003.fits) these will also be loaded as the usual convention
    in ImageJ and related imaging tools, using the last digits to sort
    the images in the stack.

    Usual type in fits is 16-bit pixel depth, data type is denoted with:
        '>i2' - uint16
        '>f2' - float16
        '>f4' - float32

    :return: sample, average flat image, average dark image

    """

    # Assumed that all images have the same size and properties as the first.
    first_sample_img = load_func(all_input_filenames[0])

    chosen_input_filenames = all_input_filenames[indices[0]:indices[1]:indices[2]] if indices else all_input_filenames

    # get the shape of all images
    img_shape = first_sample_img.shape

    # forward all arguments to internal class for easy re-usage
    il = ImageLoader(load_func, chosen_input_filenames, input_path_flat, input_path_dark, img_format, img_shape,
                     data_dtype, cores, chunksize, parallel_load, indices, construct_sinograms, progress)

    # we load the flat and dark first, because if they fail we don't want to
    # fail after we've loaded a big stack into memory
    flat_avg, flat_filenames = il.load_and_avg_data(input_path_flat, "Flat")

    dark_avg, dark_filenames = il.load_and_avg_data(input_path_dark, "Dark")

    sample_data = il.load_sample_data(chosen_input_filenames)

    # if this is true, then the loaded sample data was created via the stack_loader
    if isinstance(sample_data, Images):
        sample_data = sample_data.sample

    return Images(sample_data, flat_avg, dark_avg, all_input_filenames, indices, flat_filenames, dark_filenames)


class ImageLoader(object):
    def __init__(self,
                 load_func,
                 input_file_names,
                 input_path_flat,
                 input_path_dark,
                 img_format,
                 img_shape,
                 data_dtype,
                 cores,
                 chunksize,
                 parallel_load,
                 indices,
                 construct_sinograms,
                 progress=None):
        self.load_func = load_func
        self.input_file_names = input_file_names
        self.input_path_flat = input_path_flat
        self.input_path_dark = input_path_dark
        self.img_format = img_format
        self.img_shape = img_shape
        self.data_dtype = data_dtype
        self.cores = cores
        self.chunksize = chunksize
        self.parallel_load = parallel_load
        self.indices = indices
        self.construct_sinograms = construct_sinograms
        self.progress = progress

    def load_sample_data(self, input_file_names):
        # determine what the loaded data was
        if len(self.img_shape) == 2:
            # the loaded file was a single image
            sample_data = self.load_files(input_file_names, "Sample")
        elif len(self.img_shape) == 3:
            # the loaded file was a file containing a stack of images
            sample_data = stack_loader.execute(self.load_func,
                                               input_file_names[0],
                                               self.data_dtype,
                                               "Sample",
                                               self.cores,
                                               self.chunksize,
                                               self.parallel_load,
                                               self.indices,
                                               progress=self.progress)
        else:
            raise ValueError("Data loaded has invalid shape: {0}", self.img_shape)

        return sample_data

    def load_and_avg_data(self, file_path, name=None) -> Union[Tuple[np.ndarray, List[str]], Tuple[None, None]]:
        if file_path:
            file_names = get_file_names(file_path, self.img_format)

            data = self.load_files(file_names, name)
            return _get_data_average(data), file_names
        return None, None

    def _do_files_load_seq(self, data, files, name):
        progress = Progress.ensure_instance(self.progress, num_steps=len(files), task_name='Load')

        num_images = len(files)
        progress.add_estimated_steps(num_images)

        with progress:
            for idx, in_file in enumerate(files):
                try:
                    _inplace_load(data[idx], in_file, self.load_func)
                    progress.update(msg='Image {} of {}'.format(idx, num_images))
                except ValueError as exc:
                    raise ValueError("An image has different width and/or height "
                                     "dimensions! All images must have the same "
                                     "dimensions. Expected dimensions: {0} Error "
                                     "message: {1}".format(self.img_shape, exc))
                except IOError as exc:
                    raise RuntimeError("Could not load file {0}. Error details: " "{1}".format(in_file, exc))

        return data

    def _do_files_sinogram_load_seq(self, data, files, name):
        progress = Progress.ensure_instance(self.progress, num_steps=len(files), task_name='Sinogram Load')

        progress.add_estimated_steps(len(files))

        with progress:
            for idx, in_file in enumerate(files):
                try:
                    _inplace_load(data[:, idx, :], in_file, self.load_func)
                    progress.update(msg=name)
                except ValueError as exc:
                    raise ValueError("An image has different width and/or height "
                                     "dimensions! All images must have the same "
                                     "dimensions. Expected dimensions: {0} Error "
                                     "message: {1}".format(self.img_shape, exc))
                except IOError as exc:
                    raise RuntimeError("Could not load file {0}. Error details: " "{1}".format(in_file, exc))

        return data

    def _do_files_load_par(self, data, files, name):
        f = ptsm.create_partial(_inplace_load, ptsm.inplace, load_func=self.load_func)

        ptsm.execute(data, files, f, self.cores, self.chunksize, name, self.progress)
        return data

    def load_files(self, files, name=None):
        # Zeroing here to make sure that we can allocate the memory.
        # If it's not possible better crash here than later.
        data = self.allocate_data(num_images=len(files))

        if self.construct_sinograms:
            return self._do_files_sinogram_load_seq(data, files, name)
        elif self.parallel_load:
            return self._do_files_load_par(data, files, name)
        else:
            return self._do_files_load_seq(data, files, name)

    def allocate_data(self, num_images):
        if self.construct_sinograms:
            return pu.create_shared_array((self.img_shape[0], num_images, self.img_shape[1]), dtype=self.data_dtype)
        else:
            return pu.create_shared_array((num_images, self.img_shape[0], self.img_shape[1]), dtype=self.data_dtype)


def _inplace_load(data, filename, load_func=None):
    data[:] = load_func(filename)


def _get_data_average(data):
    return np.mean(data, axis=0)
