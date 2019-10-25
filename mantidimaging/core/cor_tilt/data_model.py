from enum import Enum
from logging import getLogger

import numpy as np
import scipy as sp

from mantidimaging.core.data import const

from .angles import cors_to_tilt_angle

LOG = getLogger(__name__)


class Field(Enum):
    SLICE_INDEX = 0
    CENTRE_OF_ROTATION = 1


FIELD_NAMES = {Field.SLICE_INDEX: 'Slice Index', Field.CENTRE_OF_ROTATION: 'COR'}


class CorTiltDataModel(object):
    """
    Data model for COR/Tilt finding from (slice index, centre of rotation) data
    pairs.
    """
    _cached_gradient: float
    _cached_cor: float

    def __init__(self):
        self._points = []
        self._cached_gradient = 0.0
        self._cached_cor = 0.0

    def populate_slice_indices(self, begin, end, count, cor=0.0):
        self.clear_results()

        self._points = [[int(idx), cor] for idx in np.linspace(begin, end, count, dtype=int)]
        LOG.debug('Populated slice indices: {}'.format(self.slices))

    def linear_regression(self):
        LOG.debug('Running linear regression with {} points'.format(self.num_points))
        result = sp.stats.linregress(self.slices, self.cors)
        self._cached_gradient, self._cached_cor = result[:2]

    def add_point(self, idx=None, slice_idx=0, cor=0.0):
        self.clear_results()

        if idx is None:
            self._points.append([slice_idx, cor])
        else:
            self._points.insert(idx, [slice_idx, cor])

    def set_point(self, idx, slice_idx=None, cor=None):
        self.clear_results()

        if slice_idx is not None:
            self._points[idx][Field.SLICE_INDEX.value] = int(slice_idx)

        if cor is not None:
            self._points[idx][Field.CENTRE_OF_ROTATION.value] = float(cor)

    def _get_data_idx_from_slice_idx(self, slice_idx):
        for i, p in enumerate(self._points):
            if int(p[Field.SLICE_INDEX.value]) == slice_idx:
                return i
        return None

    def set_cor_at_slice(self, slice_idx, cor):
        data_idx = self._get_data_idx_from_slice_idx(slice_idx)
        self.set_point(data_idx, cor=cor)

    def remove_point(self, idx):
        self.clear_results()
        del self._points[idx]

    def clear_points(self):
        self._points = []
        self.clear_results()

    def clear_results(self):
        self._cached_gradient = 0.0
        self._cached_cor = 0.0

    def point(self, idx):
        return self._points[idx] if idx < self.num_points else None

    def sort_points(self):
        self._points.sort(key=lambda p: p[Field.SLICE_INDEX.value])

    def get_cor_for_slice(self, slice_idx):
        a = [p[Field.CENTRE_OF_ROTATION.value] for p in self._points if p[Field.SLICE_INDEX.value] == slice_idx]
        return a[0] if a else None

    def get_cor_for_slice_from_regression(self, slice_idx):
        if not self.has_results:
            return None

        cor = (self.gradient * slice_idx) + self.cor
        return cor

    @property
    def slices(self):
        return [int(p[Field.SLICE_INDEX.value]) for p in self._points]

    @property
    def cors(self):
        return [float(p[Field.CENTRE_OF_ROTATION.value]) for p in self._points]

    @property
    def gradient(self):
        return self._cached_gradient

    @property
    def cor(self):
        return self._cached_cor

    @property
    def angle_rad(self):
        return cors_to_tilt_angle(self.slices[-1], self.gradient)

    @property
    def has_results(self):
        return self._cached_gradient is not None and self._cached_cor is not None

    @property
    def empty(self):
        return not self._points

    @property
    def num_points(self):
        return len(self._points)

    @property
    def stack_properties(self):
        return {
            const.COR_TILT_ROTATION_CENTRE: float(self.cor),
            const.COR_TILT_FITTED_GRADIENT: float(self.gradient),
            const.COR_TILT_TILT_ANGLE_RAD: float(self.angle_rad),
            const.COR_TILT_SLICE_INDICES: self.slices,
            const.COR_TILT_ROTATION_CENTRES: self.cors
        }
