from collections.abc import Iterable
from dataclasses import dataclass
from typing import Union, List

from mantidimaging.core.utility.close_enough_point import CloseEnoughPoint


@dataclass
class SensibleROI(Iterable):
    __slots__ = ("left", "top", "right", "bottom")
    left: int
    top: int
    right: int
    bottom: int

    @staticmethod
    def from_points(position: CloseEnoughPoint, size: CloseEnoughPoint) -> 'SensibleROI':
        return SensibleROI(position.x, position.y, position.x + size.x, position.y + size.y)

    @staticmethod
    def from_list(roi: Union[List[int], List[float]]):
        return SensibleROI(int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3]))

    def __iter__(self):
        """
        Allows unpacking the ROI with `*roi`
        :return: Iterable of all ROI parts
        """
        return iter((self.left, self.top, self.right, self.bottom))

    def __str__(self):
        return f"Left: {self.left}, Top: {self.top}, Right: {self.right}, Bottom: {self.bottom}"

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top
