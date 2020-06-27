import json
import pprint
from copy import deepcopy
from typing import List, Tuple, Optional, Any, Dict

import numpy as np

from mantidimaging.core.operation_history import const
from mantidimaging.core.parallel import utility as pu


class Images:
    NO_FILENAME_IMAGE_TITLE_STRING = "Image: {}"

    def __init__(self,
                 sample: np.ndarray,
                 flat: np.ndarray = None,
                 dark: np.ndarray = None,
                 sample_filenames: Optional[List[str]] = None,
                 indices: Optional[Tuple[int, int, int]] = None,
                 flat_filenames: Optional[List[str]] = None,
                 dark_filenames: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 sinograms: bool = False,
                 sample_memory_file_name: Optional[str] = None,
                 flat_memory_file_name: Optional[str] = None,
                 dark_memory_file_name: Optional[str] = None):
        """

        :param sample: Images of the Sample/Projection data
        :param flat: Images of the Flat data
        :param dark: Images of the Dark data
        :param sample_filenames: All filenames that were matched for loading
        :param indices: Indices that were actually loaded
        :param flat_filenames: All filenames that were matched for loading of Flat images
        :param dark_filenames: All filenames that were matched for loading of Dark images
        :param metadata: Properties to copy when creating a new stack from an existing one
        """

        self.sample = sample
        self.flat = flat
        self.dark = dark
        self.indices = indices

        self._filenames = sample_filenames
        self.flat_filenames = flat_filenames
        self.dark_filenames = dark_filenames

        self.metadata: Dict[str, Any] = deepcopy(metadata) if metadata else {}
        self.sinograms = sinograms

        self.sample_memory_file_name = sample_memory_file_name
        self.flat_memory_file_name = flat_memory_file_name
        self.dark_memory_file_name = dark_memory_file_name

    def __str__(self):
        return 'Image Stack: sample={}, flat={}, dark={}, |properties|={}'.format(
            self.sample.shape if self.sample is not None else None, self.flat.shape if self.flat is not None else None,
            self.dark.shape if self.dark is not None else None, len(self.metadata))

    def count(self) -> int:
        return len(self._filenames) if self._filenames else 0

    def free_memory(self):
        self.free_sample()
        self.free_flat()
        self.free_dark()

    def free_sample(self):
        if self.sample_memory_file_name is not None:
            pu.delete_shared_array(self.sample_memory_file_name)
        self.sample = None

    def free_flat(self):
        if self.flat_memory_file_name is not None:
            pu.delete_shared_array(self.flat_memory_file_name)
        self.flat = None

    def free_dark(self):
        if self.dark_memory_file_name is not None:
            pu.delete_shared_array(self.dark_memory_file_name)
        self.dark = None

    @property
    def filenames(self) -> Optional[List[str]]:
        return self._filenames

    @filenames.setter
    def filenames(self, new_ones: List[str]):
        assert len(new_ones) == self.sample.shape[0], "Number of filenames and number of images must match."
        self._filenames = new_ones

    @property
    def has_history(self) -> bool:
        return const.OPERATION_HISTORY in self.metadata

    @property
    def metadata_pretty(self):
        pp = pprint.PrettyPrinter(indent=2)
        return pp.pformat(self.metadata)

    def load_metadata(self, f):
        self.metadata = json.load(f)

    def save_metadata(self, f):
        json.dump(self.metadata, f)

    def record_operation(self, func_name: str, display_name=None, *args, **kwargs):
        if const.OPERATION_HISTORY not in self.metadata:
            self.metadata[const.OPERATION_HISTORY] = []

        def accepted_type(o):
            return type(o) in [str, int, float, bool, tuple, list]

        self.metadata[const.OPERATION_HISTORY].append({
            const.OPERATION_NAME:
                func_name,
            const.OPERATION_ARGS: [a if accepted_type(a) else None for a in args],
            const.OPERATION_KEYWORD_ARGS: {k: v
                                           for k, v in kwargs.items() if accepted_type(v)},
            const.OPERATION_DISPLAY_NAME:
                display_name
        })

    def copy(self, flip_axes=False):
        import uuid
        from copy import deepcopy
        sample_name = f"{uuid.uuid4()}"
        # flat_name = f"{uuid.uuid4()}-Flat"
        # dark_name = f"{uuid.uuid4()}-Dark"
        shape = (self.sample.shape[1], self.sample.shape[0], self.sample.shape[2]) if flip_axes else self.sample.shape
        sample_copy = pu.create_shared_array(f"{sample_name}", shape, self.sample.dtype)
        if flip_axes:
            sample_copy[:] = np.swapaxes(self.sample, 0, 1)
        else:
            sample_copy[:] = self.sample[:]

        images = Images(sample_copy,
                        sample_memory_file_name=sample_name,
                        indices=deepcopy(self.indices),
                        metadata=deepcopy(self.metadata),
                        sinograms=deepcopy(self.sinograms))
        return images

    @property
    def width(self):
        if not self.sinograms:
            return self.sample.shape[1]
        else:
            return self.sample.shape[0]

    @property
    def height(self):
        return self.sample[2]

    def sino(self, slice_idx) -> np.ndarray:
        if not self.sinograms:
            return np.swapaxes(self.sample, 0, 1)[slice_idx]
        else:
            return self.sample[slice_idx]
    # def to_sino(self, deepcopy=False):
    #     if not self.sinograms:
    #         return np.swapaxes(self.sample, 0, 1)
    #     else:
    #         return self.sample
